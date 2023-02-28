# Ember motif for the BFS ISB

This directoroy contains code to help you use the Ember BFS motif. The motif is in the devel branch of sst-elements.

## Data collection

The models in this directory were trained on data collected from Cori. We collected data on `16-24` nodes, on `4-64` ranks, for `1-4` threads.


## Usage

Once you have pulled the devel branch of sst-elements, you can use the sdl file in this directory to run experiments as follows:

```bash
sst cori-simple.py --model-options="<N> <threads> <size> <version>"

# N: The number of nodes to simulate. Must be square.
# threads: The number of threads per rank to simulate.
#   Must be 1-4 if using polynomial models, and 1 otherwise
# size:    The scale of the R-MAT graph to simulate running BFS on
# version: Either exponential, polynomial, or trace. Described further below.

```
## Files

You will find two types of model files in the `models/` subdirectory. Each run of the simulation needs two model files: a message size model and a compute time model. The `cori-simple.py` sdl file takes care of setting these up for you when you select a version. Message size models are needed for each _callsite_ in a simulation, which you can think of as a single MPI call in the original ISB. Compute time models are needed for each _callsite transition_, which represents the compute that happened between two MPI calls.

## Model Version

We have implemented three different types of models, polynomial, exponential, and trace.

__polynomial__: The polynomial models 4-th order polynomials. There is a separate model for each callsite or callsite transition, and a separate model for 1, 2, 3 or 4 threads per rank. An example from the polynomial execution time model, `models/exec_poly.model`:

```
callsite_source callsite_destination threads_per_rank 0,0 1,0 0,1 2,0 1,1 0,2 3,0 2,1 1,2 0,3 4,0 3,1 2,2 1,3 0,4
1 2 1 -6890.8582 1593.4272 -17.5702 -136.3303 2.3121 0.0652 5.0886 -0.0351 -0.0328 0.0036 -0.0691 -0.0027 0.0021 -0.0003 0.0
```

The file header and the first model are shown. The first three columns define the callsite transition and the number of threads. Furhter columns are the coefficients in the polynomial. A coefficient A in column X,Y means the term A\*size\^X\*nodes\^Y is in the polynomial. For isntance, in the above example, the constant term is `-6890.8582`.

__exponential__: The exponential models contain one optimization not seen in the polynomial models: callsites with constant message size are modeled seaparately, wherease everything is a polynomial in the previous models. Here is an exceprt from `modesl/exec_exp.model`:
```
40 1 CONSTANT 8
41 1 EXPONENTIAL -0.00011642487754581765 -0.032057240406750065 0.6549694330697653 -4.121717354301114
```

In this example, callsite 40, with 1 thread, has a constant value of 8. Callsite 41 however, is modeled with an exponential fit. These coefficients define the following model:

```
msg_size = exp(A*nodes*size + B*nodes + C*size + D)
```

__trace__: The trace models are direct translationsn of the MPI traces we collected on Cori. These serve as a sort of upper bound on the accuracy of the other models. The caveat is that currently each simulated rank reads the rank 0 MPI trace. This can be remedied in the future if there is interest in this approach.

Here is an example of a model from `models/trace/bfs_msgtrace_4-4-1-16-0.txt`:

```
28 1 TRACE 0.0 32.0 0.0 0.0 4.0

```
This means that callsite 28, which represents an MPI call, sent messages of size 0, 32, 0, 0, 4 the first 5 times it was run. These models cannot scale beyond what we have traces for, unlike the exponential and polynomial traces.

## Scaling Experiments

You can use the `scaling.py` script to run a series of simulations to test how the models scale. By default, it will run input sizes `16-24` on `4-64` nodes. The output should be easily parsed by `pandas`.

```
./scaling.py <version>
```
