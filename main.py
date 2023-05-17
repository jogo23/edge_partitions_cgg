"""
Edge Partitions of Complete Geometric Graphs.
Given a complete straight-line graph, this program partitions the
edge set into plane spanning trees or plane subgraphs.

MIT License

Copyright (c) 2023 Johannes Obenaus

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import argparse

from helper import str2bool
from solver import Solver_ILP


##################################################################################
# Examples (see also Readme in git repository)
##################################################################################

# python main.py

# python main.py --pset bw --k 3 --l 3 --partition_pst True --no_save True
# python main.py --pset bw --k 3 --l 3 --partition_pst True --no_save True --draw_labels True
# python main.py --pset bw --k 3 --l 3 --partition_pst True --no_save True --plot False
# python main.py --pset bw --k 5 --l 3 --partition_pst True

# python main.py --pset bw --k 3 --l 5 --n1_constraints True --forbidden_cycles 3
# python main.py --pset bw --k 3 --l 5 --partition_subgraphs True

# python main.py --pset convex --n 16 --partition_pst True --no_save True
# python main.py --pset random --n 14 --partition_pst True
# python main.py --pset random_wheel --n 14 --partition_pst True
# python main.py --pset two_convex_layers --n 14 --partition_pst True

# (12min) python main.py --pset gw --group_sizes 2 3 3 4 5 --n1_constraints True --forbidden_cycles 3 4
# python main.py --pset gw --group_sizes 2 3 4 3 5 --partition_pst True
# python main.py --pset gw --group_sizes 4 5 6 --partition_pst True
# (4min) python main.py --pset gw --group_sizes 5 6 6 --n1_constraints True --forbidden_cycles 3

# python main.py --pset convex --n 15 --k_planar 1 --n_colors 5 --partition_subgraphs True
# python main.py --pset convex --n 15 --k_planar 1 --n_colors 4 --partition_subgraphs True

# python main.py --rand_exp_pst True --pset random --n 12 --n_iterations 5
# python main.py --rand_exp_pst True --pset random_wheel --n 14 --n_iterations 10
# python main.py --rand_exp_subgraphs True --pset random --n 16 --n_iterations 10
# python main.py --rand_exp_subgraphs True --pset random --n 18 --n_iterations 20

##################################################################################


def main():

    args = parse_input()

    if args.rand_exp_pst:
        random_experiment_pst(args)
        return

    if args.rand_exp_subgraphs:
        random_experiment_subgraphs(args)
        return

    ilp_solver = Solver_ILP(args)
    ilp_solver.compute_solution()


def random_experiment_pst(args):

    for _ in range(args.n_iterations):
        ilp_solver = Solver_ILP(args)
        ilp_solver.compute_solution()


def random_experiment_subgraphs(args):

    for _ in range(args.n_iterations):
        ilp_solver = Solver_ILP(args)
        ilp_solver.compute_solution()


def parse_input():

    parser = argparse.ArgumentParser(description="ILP stuff")

    # point set configuration
    parser.add_argument("--pset", type=str, default="bw", help="bw, gw, convex, random, random_wheel, two_convex_layers")
    parser.add_argument("--k", type=int, default=3, help="k in BW_{k,l}")
    parser.add_argument("--l", type=int, default=3, help="l in BW_{k,l}")
    parser.add_argument("--n", type=int, default=-1, help="not needed for bw and gw")
    parser.add_argument("--group_sizes", type=int, nargs="*", default=[], help="group sizes for gw")

    # master configs (if set to True, the following commands overrule certain settings)
    parser.add_argument("--partition_pst", type=str2bool, default=False, help="sets all commands for PST partition.")
    parser.add_argument("--partition_subgraphs", type=str2bool, default=False, help="partition into subgraphs.")
    parser.add_argument("--rand_exp_pst", type=str2bool, default=False, help="")
    parser.add_argument("--rand_exp_subgraphs", type=str2bool, default=False, help="")
    parser.add_argument("--n_iterations", type=int, default=5, help="number of iterations for random experiments")

    # ILP constraints and ILP parameters
    parser.add_argument("--n1_constraints", type=str2bool, default=True, help="constraint: n-1 edges.")
    parser.add_argument("--forbidden_cycles", type=int, nargs="*", default=[], help="forbidden cycles, can be empty.")
    parser.add_argument("--cover_all_vertices", type=str2bool, default=False, help="constraint: all vertices reached.")
    parser.add_argument("--timelimit", type=int, default=None, help="timelimit for ILP in seconds (86400 sec = 1 day)")

    # k-planar partitions
    parser.add_argument("--k_planar", type=int, default=-1, help="partition into k-planar subgraphs")

    # plotting
    parser.add_argument("--plot", type=str2bool, default=True, help="show interactive plots.")
    parser.add_argument("--draw_labels", type=str2bool, default=False, help="draw labels on points and edges")

    # saving meta data and results
    parser.add_argument("--save_data", type=str2bool, default=True, help="save basic data and results")
    parser.add_argument("--save_data_overview", type=str2bool, default=False, help="save data as overview")
    parser.add_argument("--res_dir", type=str, default="results", help="directory for basic results")
    parser.add_argument("--no_save", type=str2bool, default=False, help="dont save anything")

    # miscellanious
    parser.add_argument("--n_colors", type=int, default=-1, help="number of available colors (default is n//2)")
    parser.add_argument("--check_pst", type=str2bool, default=False, help="checks whether partition is PST.")

    args = parser.parse_args()

    if args.no_save:
        args.save_data = False
        args.save_data_overview = False

    # setup for running experiment partitioning random pointsets
    if args.rand_exp_pst or args.rand_exp_subgraphs:
        # args.pset = "random"
        args.save_data = False
        args.save_data_overview = True
        args.plot = False
        args.partition_pst = True if args.rand_exp_pst else False
        args.partition_subgraphs = True if args.rand_exp_subgraphs else False

    if args.partition_pst:
        args.n1_constraints = True
        if args.forbidden_cycles == []:
            args.forbidden_cycles = [3, 4]
        args.cover_all_vertices = True
        args.check_pst = True

    if args.partition_subgraphs:
        args.n1_constraints = False
        args.forbidden_cycles = []
        args.cover_all_vertices = False

    assert args.partition_pst == False or args.partition_subgraphs == False
    for l in args.forbidden_cycles:
        assert l == 3 or l == 4

    return args


if __name__ == "__main__":
    main()
