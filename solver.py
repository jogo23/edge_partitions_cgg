from abc import ABC, abstractmethod
from datetime import datetime
import itertools
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import gurobipy as grb
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_pdf import PdfPages
import networkx as nx

from helper import do_intersect, generate_all_cycles, get_input, in_general_position

NX_OPTIONS_NORMAL = {
    "node_color": "black",
    "with_labels": False,
    "node_size": 40,
    "width": 1.5,
}

NX_OPTIONS_LABELS = {
    "font_size": 8,
    "node_size": 80,
    "node_color": "black",
    "edgecolors": "black",
    "font_color": "whitesmoke",
    "linewidths": 1,
    "width": 1.5,
}

ALL_COLORS = list(mcolors.TABLEAU_COLORS) + list(mcolors.BASE_COLORS)


class SolverBase(ABC):
    """
    Base class that provides basic methods for plotting, saving, etc.
    All solvers should inherit from SolverBase and must implement the
    method compute_solution().
    """
    def __init__(self, args) -> None:

        self.args = args

        self.points, self.edges = get_input(args)
        assert(in_general_position(self.points))

        self.n = len(self.points)
        self.k = self.n // 2 if args.n_colors < 0 else args.n_colors
        self.colorclasses_nx = []

        if self.args.draw_labels:
            self.nx_options = NX_OPTIONS_LABELS
        else:
            self.nx_options = NX_OPTIONS_NORMAL

        self.cur_time_string = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
        self.meta_data = dict()
        self._set_initial_meta_data()

    @abstractmethod
    def compute_solution(self):
        pass
    
    def _set_initial_meta_data(self) -> None:
        self.meta_data["n"] = self.n
        self.meta_data["coors"] = [(p.x, p.y) for p in self.points]
        params_string = " ".join([f"--{arg} {getattr(self.args, arg)}" for arg in vars(self.args)])
        self.meta_data["command_line_string"] = params_string

    def plot_and_save_fig(self) -> None:

        assert len(self.colorclasses_nx) > 0
        if self.args.save_data:
            pre_path = self.prepare_directory(self.args.res_dir)  # default is 'results'
            pp = PdfPages(pre_path + "_multipage.pdf")

        plt.figure()
        for i, G in enumerate(self.colorclasses_nx):
            nx.draw_networkx(
                G, pos={v: G.nodes[v]["pos"] for v in G.nodes}, edge_color=ALL_COLORS[i], **self.nx_options
            )
        if self.args.save_data:
            plt.savefig(pp, format="pdf")
        if self.args.plot:
            plt.show()

        for i, G in enumerate(self.colorclasses_nx):
            plt.figure()
            nx.draw_networkx(
                G, pos={v: G.nodes[v]["pos"] for v in G.nodes}, edge_color=ALL_COLORS[i], **self.nx_options
            )
            if self.args.draw_labels:
                nx.draw_networkx_edge_labels(
                    G, pos={v: G.nodes[v]["pos"] for v in G.nodes}, edge_labels={e: i for i, e in enumerate(G.edges)}
                )
            if self.args.save_data:
                plt.savefig(pp, format="pdf")
            if self.args.plot:
                plt.show()

        if self.args.save_data:
            pp.close()
        plt.close()

    def prepare_directory(self, directory) -> str:

        if not os.path.exists(directory):
            os.mkdir(directory)

        pre_path = str(Path(directory) / self.cur_time_string)
        return pre_path

    def save_results(self) -> None:

        pre_path = self.prepare_directory(self.args.res_dir)  # default is 'results'

        self.model.write(pre_path + "_ilp.json")
        if self.model.Status == grb.GRB.OPTIMAL:
            self.model.write(pre_path + "_ilp.sol")

        with open(pre_path + "_data.json", "w", encoding="utf-8") as f:
            json.dump(self.meta_data, f, ensure_ascii=False)

    def save_no_sol_found(self) -> None:
        if self.args.save_data:
            self.save_results()

        if self.args.save_data_overview:
            self.save_overview()

    def save_overview(self) -> None:
        """
        saves the following information:
            - timestamp
            - n
            - point coors (random), k,l (bw), group_sizes (gw)
            - solution found (runtime)
            - is PST partition
        """

        directory = "results_overview"
        if not os.path.exists(directory):
            os.mkdir(directory)

        filename = f"{self.args.pset}_{self.n}_{'pst' if self.args.check_pst else 'subgraphs'}.txt"
        save_path = Path(directory) / filename

        # found an input that cannot be partitioned
        if self.model.Status == 3:
            with open(directory + "/important.txt", "a+") as f:
                for p in self.points:
                    f.write(str(p.x) + " " + str(p.y) + " ")
                f.write("\n")
                f.write(f"no solution (Runtime: {self.model.Runtime})\n")
                f.write("----------------------" + "\n")

        with open(save_path, "a+") as f:
            f.write(self.cur_time_string + "\n")
            f.write(str(self.n) + "\n")

            if self.args.pset == "bw":
                f.write(f"k = {self.args.k}, l = {self.args.l}")
            elif self.args.pset == "gw":
                for x in self.args.group_sizes:
                    f.write(str(x) + " ")
            else:
                for p in self.points:
                    f.write(str(p.x) + " " + str(p.y) + " ")
            f.write("\n")

            if self.model.Status == 2:
                f.write(f"solution found (Runtime: {self.model.Runtime})\n")
            elif self.model.Status == 3:
                f.write(f"no solution (Runtime: {self.model.Runtime})\n")
            else:
                f.write(f"unknown (Runtime: {self.model.Runtime})\n")

            f.write("is PST partition = " + str(self.is_pst_partition()) + "\n")
            f.write("----------------------" + "\n")

        print(f"Saved overview results to {save_path}\n")

    def convert_edge_colors_to_nx(self) -> None:

        for e in self.edges:
            assert e.color is not None

        for c in range(self.k):
            G = nx.Graph()
            G.add_nodes_from((p.id, {"pos": (p.x, p.y)}) for p in self.points)

            G.add_edges_from([(e.p.id, e.q.id) for e in self.edges if e.color == c])

            self.colorclasses_nx.append(G)

    def is_pst(self, G) -> bool:
        if len(G.edges) != len(G.nodes) - 1:
            return False
        if not nx.is_connected(G):
            return False
        return True

    def is_pst_partition(self) -> bool:
        if len(self.colorclasses_nx) == 0:
            return False
        for G in self.colorclasses_nx:
            if not self.is_pst(G):
                return False
        return True


class Solver_ILP(SolverBase):
    def __init__(self, args) -> None:
        super().__init__(args)

    def compute_solution(self) -> None:

        print("Started building the ILP model...")
        self.model, self.x_vars = self._graph_to_ilp_model()

        if self.args.timelimit is not None:
            self.model.Params.timelimit = self.args.timelimit

        print("Started solving the model...")
        self.model.optimize()

        print(f"Status of the model: {self.model.Status} (2 = optimal, 3 = infeasible)")

        if self.model.Status != grb.GRB.OPTIMAL:
            print("Did not find a solution")
            self.save_no_sol_found()
            return

        self._ilp_model_to_edge_color_assignment()
        self.convert_edge_colors_to_nx()

        if self.args.save_data:
            self.save_results()

        if self.args.save_data_overview:
            self.save_overview()

        if self.args.plot or self.args.save_data:
            self.plot_and_save_fig()

        # double check that graph classes are plane spanning trees
        if self.args.check_pst and not self.is_pst_partition():
            print("Partition is not a partition into PST.")

    def _ilp_model_to_edge_color_assignment(self) -> None:
        """assign results from ILP model to edge colors"""
        for v, colors in self.x_vars.items():
            for c, var in colors.items():
                if var.X == 1:
                    self.edges[v].color = c

    def _graph_to_ilp_model(self) -> Tuple[grb.Model, Dict]:
        """
        Convert graph (given by self.edges) to ILP model.
        Returns:
            ILP model, ILP variables
        """

        edges = self.edges
        k = self.k
        n = self.n
        n_edges = len(self.edges)

        model = grb.Model(name="graph partitioning")

        # create lookup dictionary
        edge_tuple_to_id = dict()
        for e in edges:
            edge_tuple_to_id[(e.p.id, e.q.id)] = e.id
            edge_tuple_to_id[(e.q.id, e.p.id)] = e.id

        # define model variables as
        # x_{e}_{c} such that x_e_c = 1 <==> edge e receives color c
        x_vars = {
            e: {c: model.addVar(vtype=grb.GRB.BINARY, name="x_{}_{}".format(e, c)) for c in range(k)}
            for e in range(n_edges)
        }

        # CONSTRAINT 1 (mandatory): each edge receives exactly one color
        for e in range(n_edges):
            model.addLConstr(
                lhs=grb.quicksum(x_vars[e][c] for c in range(k)),
                sense=grb.GRB.EQUAL,
                rhs=1,
                name=f"constr_{e}",
            )

        # CONSTRAINT 2 (mandatory): intersecting edges get different colors
        if self.args.k_planar <= 0:  # plane partition
            for e1, e2 in itertools.combinations(edges, 2):
                if not do_intersect(e1, e2):
                    continue
                for c in range(k):
                    model.addLConstr(
                        lhs=grb.quicksum((x_vars[e1.id][c], x_vars[e2.id][c])),
                        sense=grb.GRB.LESS_EQUAL,
                        rhs=1,
                        name=f"neighbor_constr_{e1.id}:{e2.id}_{c}",
                    )
        else:  # k-plane partition
            for c in range(k):
                for e in edges:
                    model.addLConstr(
                        lhs=grb.quicksum(x_vars[e1.id][c] for e1 in e.crossed_edges),
                        sense=grb.GRB.LESS_EQUAL,
                        rhs=(self.args.k_planar + (1 - x_vars[e.id][c]) * len(edges)),
                        name=f"neighbor_constr_{e.id}_{c}",
                    )

        # CONSTRAINT 3 (optional): each color class has exactly n-1 edges
        if self.args.n1_constraints:
            for c in range(k):
                model.addLConstr(
                    lhs=grb.quicksum(x_vars[e][c] for e in range(n_edges)),
                    sense=grb.GRB.EQUAL,
                    rhs=n - 1,
                    name=f"constr_{c}",
                )

        # CONSTRAINT 4 (optional): forbid cycles of certain lengths
        forbidden_lengths = self.args.forbidden_cycles  # only 3 and 4 possible at the moment
        all_cycles: List[Tuple[int, ...]] = generate_all_cycles(n, forbidden_lengths)

        for cycle in all_cycles:
            # get edge ids of the edges involved in the cycle
            edge_ids = []
            for i in range(len(cycle)):
                s = cycle[i]
                t = cycle[(i + 1) % len(cycle)]
                edge_ids.append(edge_tuple_to_id[(s, t)])

            # cycle must not be monochromatic
            for color in range(k):
                model.addLConstr(
                    lhs=grb.quicksum([x_vars[i][color] for i in edge_ids]),
                    sense=grb.GRB.LESS_EQUAL,
                    rhs=len(cycle) - 1,
                    name=f"{len(cycle)}_cycle_constr_{cycle}_color_{c}",
                )

        # CONSTRAINT 5 (optional): every vertex is incident to at least one edge of each color
        if self.args.cover_all_vertices:
            for c in range(k):
                for v in range(n):
                    incident_edge_ids = [e.id for e in edges if e.p.id == v or e.q.id == v]
                    model.addLConstr(
                        lhs=grb.quicksum(x_vars[e][c] for e in incident_edge_ids),
                        sense=grb.GRB.GREATER_EQUAL,
                        rhs=1,
                        name=f"constr_{c}",
                    )

        objective = grb.quicksum(x_vars[e][c] for e in range(n_edges) for c in range(k))

        model.ModelSense = grb.GRB.MINIMIZE
        model.setObjective(objective)

        return model, x_vars
