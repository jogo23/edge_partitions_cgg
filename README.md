# Edge partitions of Complete Geometric Graphs

This is the code accompanying my phd thesis, which I used for the chapter concerning edge partitions of complete geometric graphs. See also our paper [Edge Partitions of Complete Geometric Graphs](https://drops.dagstuhl.de/opus/volltexte/2022/16014/).

## What does this program do?

Given a set $P$ of $2n$ points in general position in the plane, the program computes a partition of the edges of the corresponding complete straight-line graph on $P$ into plane spanning trees or plane subgraphs. In other words, the $\binom{2n}{2}$ straight-line edges are colored with $n$ colors such that every color class forms a plane spanning tree or a plane subgraph. If such a partition does not exist, the program reports an infeasible ILP.

ATTENTION: The main purpose of this code is proving that there exist point sets which do not admit a partition into plane spanning trees. Hence, in order to save a huge amount of constraints in our ILP formulation, we implemented only part of the constraints enforcing the properties of a spanning tree. More precisely, when partitioning into plane spanning trees we enforce the following constraints:

0. Edges of the same color do not cross (this is always enforced),
1. Every color class has precisely $n-1$ edges,
2. No color class contains a cycle of length 3 (cycles of length 4 can also be set to be forbidden).

An input that cannot even satisfy these constraints, can in particular not be partitioned into plane spanning trees. Conversely, if the program reports a solution, there is no guarantee that the color classes indeed form spanning trees (the program can check this).

## Citation
If you find this repository useful, please cite the following reference
```
@InProceedings{aichholzer_et_al:LIPIcs.SoCG.2022.6,
  author =	{Aichholzer, Oswin and Obenaus, Johannes and Orthaber, Joachim and Paul, Rosna and Schnider, Patrick and Steiner, Raphael and Taubner, Tim and Vogtenhuber, Birgit},
  title =	{{Edge Partitions of Complete Geometric Graphs}},
  booktitle =	{38th International Symposium on Computational Geometry (SoCG 2022)},
  pages =	{6:1--6:16},
  series =	{Leibniz International Proceedings in Informatics (LIPIcs)},
  ISBN =	{978-3-95977-227-3},
  ISSN =	{1868-8969},
  year =	{2022},
  volume =	{224},
  editor =	{Goaoc, Xavier and Kerber, Michael},
  publisher =	{Schloss Dagstuhl -- Leibniz-Zentrum f{\"u}r Informatik},
  address =	{Dagstuhl, Germany},
  URL =		{https://drops.dagstuhl.de/opus/volltexte/2022/16014},
  URN =		{urn:nbn:de:0030-drops-160141},
  doi =		{10.4230/LIPIcs.SoCG.2022.6},
  annote =	{Keywords: edge partition, complete geometric graph, plane spanning tree, wheel set}
}
```

## Quickstart

Python 3 and a [Gurobi](https://www.gurobi.com/) license (for solving the ILP) are required.

### Using virtualenv
Make sure you have Python 3.9 installed.
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Using conda
```
conda create -n edge_partitions python=3.9
conda activate edge_partitions
pip install -r requirements.txt
```

Setup the Gurobi license as described [here](https://www.gurobi.com/).

```
python main.py
```

## An input that cannot be partitioned

As described in the above mentioned paper, bumpy wheel $BW_{3,5}$ is an example of an input that cannot be partitioned into plane spanning trees. To run the program on this input, execute the following:

```
python main.py --pset bw --k 3 --l 5 --n1_constraints True --forbidden_cycles 3
```

## Command line arguments

- point set configurations:

`--pset` specifies the type of the underlying point set ('bw' (bumpy wheel), 'gw' (generalized wheel), 'convex', 'random', 'random_wheel', 'two_convex_layers').

`--n` specifies the total number of points of the point set (mandatory for all except bw and gw); should usually be an even integer.

`--k` and `--l` specify the group sizes if pset is bw.

`--group_sizes` specifies the sizes of the groups if pset is gw.

- ILP constraints and parameters:

`--n1_constraints` enforces $n-1$ edges in each color class.

`--forbidden_cycles` forbids cycles of certain lengths in any color class (lengths 3 and 4 are possible).

`--cover_all_vertices` enforces that there are no isolated vertices in any color class (may help the ILP to find a solution faster).

`--timelimit` sets a timelimit for the ILP.

- $k$-planar partitions

`--k_planar` allows edges to cross at most $k$ times.

- Plotting:

`--plot` show plot (true/false).

`--draw_labels` draw labels of edges and vertices (true/false).

- Saving data:

`--save_data` saves basic data concerning the configurations used, also saves the figure if a solution was found.

`--save_data_overview` only saves an overview of the results (useful when running `--rand_exp_pst` or `--rand_exp_subgraphs`).

`--res_dir` specifies the directory for the results (default is "results/").

`--no_save` if set to true, the program does not save anything.

- Miscellanious:

`--n_colors` specifies the number of available colors (default is $n/2$); useful, for example, when partitioning into $k$-plane subgraphs. 

`--check_pst` double checks whether partition is really a partition into plane spanning trees and prints a warning to the terminal if not.

- Master commands that overrule certain other commands:

`--partition_pst` sets all commands to aim for a partition into **spanning trees**.

`--partition_subgraphs` sets all commands to aim for a partition into **subgraphs**.

`--rand_exp_pst` runs experiment on random point sets for `--n_iterations` iterations; aiming to partition into spanning trees.

`--rand_exp_subgraphs` runs experiment on random point sets for `--n_iterations` iterations; aiming to partition into subgraphs.

## Examples

- Testing some command line arguments for simple bumpy wheels:

```
python main.py --pset bw --k 3 --l 3 --partition_pst True --no_save True
python main.py --pset bw --k 3 --l 3 --partition_pst True --no_save True --draw_labels True
python main.py --pset bw --k 3 --l 3 --partition_pst True --no_save True --plot False
python main.py --pset bw --k 5 --l 3 --partition_pst True
```

- Bumpy $BW_{3,5}$ cannot be partitioned into plane spanning trees but admits a partition into plane subgraphs (takes 1min to compute):

```
python main.py --pset bw --k 3 --l 5 --n1_constraints True --forbidden_cycles 3
python main.py --pset bw --k 3 --l 5 --partition_subgraphs True
```

- Some examples on point sets other than bumpy wheels (note that for `random` and `two_convex_layers` the partition is likely to **not** be a partition into spanning trees):

```
python main.py --pset convex --n 16 --partition_pst True --no_save True
python main.py --pset random --n 14 --partition_pst True
python main.py --pset random_wheel --n 14 --partition_pst True
python main.py --pset two_convex_layers --n 14 --partition_pst True
```

- Generalized wheels. 

$GW_{[2,3,3,4,5]}$ does not satisfy the condition of Theorem 2.3; yet it cannot be partitioned into plane spanning trees (takes roughly 12min to compute):
```
python main.py --pset gw --group_sizes 2 3 3 4 5 --n1_constraints True --forbidden_cycles 3 4
```

Changing the order of the groups allows a partition (1min to compute):
```
python main.py --pset gw --group_sizes 2 3 4 3 5 --partition_pst True
```

Also slightly changing $BW_{3,5}$ to $GW_{[4,5,6]}$ allows a partition (1min to compute):
```
python main.py --pset gw --group_sizes 4 5 6 --partition_pst True
```

Another example that cannot be partitioned into plane spanning trees, which conforms to Theorem 2.3 (4min to compute):
```
python main.py --pset gw --group_sizes 5 6 6 --n1_constraints True --forbidden_cycles 3
```

- $k$-plane partitions (cf. Theorem 2.5):

```
python main.py --pset convex --n 15 --k_planar 1 --n_colors 5 --partition_subgraphs True
python main.py --pset convex --n 15 --k_planar 1 --n_colors 4 --partition_subgraphs True
```

- Some random experiments:

```
python main.py --rand_exp_pst True --pset random --n 12 --n_iterations 5
python main.py --rand_exp_pst True --pset random_wheel --n 14 --n_iterations 10
python main.py --rand_exp_subgraphs True --pset random --n 16 --n_iterations 10
python main.py --rand_exp_subgraphs True --pset random --n 18 --n_iterations 20
```
