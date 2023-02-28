#!/usr/bin/env python
#
# Copyright 2009-2023 NTESS. Under the terms
# of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# Copyright (c) 2009-2023, NTESS
# All rights reserved.
#
# This file is part of the SST software package. For license
# information, see the LICENSE file in the top level directory of the
# distribution.
import sst
import sys
import os
from sst.merlin.base import *
from sst.merlin.topology import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.ember import *
from sst.firefly import *


if __name__ == "__main__":

    PlatformDefinition.setCurrentPlatform("firefly-defaults")

    ### Setup the topology
    topo = topoDragonFly()
    topo.hosts_per_router = 12
    topo.routers_per_group = 32
    topo.intergroup_links = 8
    topo.num_groups = 7
    topo.link_latency = "50ns"
    topo.algorithm = "ugal"

    # Set up the routers
    router = hr_router()
    router.link_bw = "10GB/s"
    router.flit_size = "16B"
    router.xbar_bw = "16GB/s"
    router.input_latency = "60ns"
    router.output_latency = "60ns"
    router.input_buf_size = "20kB"
    router.output_buf_size = "20kB"
    router.num_vns = 1
    router.xbar_arb = "merlin.xbar_arb_lru"

    topo.router = router
    topo.link_latency = "40ns"

    ### set up the endpoint
    networkif = ReorderLinkControl()
    networkif.link_bw = "10GB/s"
    networkif.input_buf_size = "20kB"
    networkif.output_buf_size = "20kB"

    # Get the total number of network endpoints
    total_nodes = topo.getNumNodes()

    # Now define the endpoints
    if (len(sys.argv) < 5):
        print(f"Too few args ({sys.argv})")
        print("--model-options=\"<nodes> <threads_per_rank> <scale> <version>\"")
        sys.exit(1)

    # `nnodes` is the number of nodes that will be simulated
    # `threads_per_rank` is the number of threads each node will run
    #   Some models only support 1 thread currently
    # `sz` is the input to the BFS ISB, it is the R-MAT scale of the matrix
    # This sdl support using a number of models, specified by the `version` parameter:
    #    exponential: Computation and communication use an exponential model, except for constant valued message size models
    #    polynomial:  Computation and communication use a 4th order polynomial model
    #    trace:       Trace data collected from rank 0 of the program is fed into each simulated rank

    nnodes = int(sys.argv[1])
    threads_per_rank = int(sys.argv[2])
    sz = int(sys.argv[3])
    version = sys.argv[4]

    if threads_per_rank != 1 and version != 'polynomial' or threads_per_rank > 4:
        print('Polynomial models support 1-4 threads. Other modesl support 1 thread.')

    if (nnodes == 1):
        print("Error: Ember is not designed to run a single node")
        sys.exit(1)

    if (int(int(nnodes**.5)**2)!=nnodes):
        print("Error: BFS requires a square number of nodes")
        sys.exit(1)

    if (nnodes > total_nodes):
        print(f"The topology only has {total_nodes} nodes, but {nnodes} were requested")

    print(f"Running with nodes={nnodes}, threads_per_rank={threads_per_rank}, sz={sz}")

    ranks_per_node = 1 # To be added in the future
    ep = EmberMPIJob(1, nnodes, ranks_per_node)
    ep.network_interface = networkif

    # Add motifs to the simulation
    ep.addMotif("Init")

    if version == "exponential":
        msg_model  = 'models/msg_exp.model'
        exec_model = 'models/exec_exp.model'
        ep.addMotif(f"BFS sz={sz} seed=12 nodes={nnodes} threads={threads_per_rank} msg_model={msg_model} exec_model={exec_model}")

    elif version == "polynomial":
        msg_model  = 'models/msg_poly.model'
        exec_model = 'models/exec_poly.model'
        ep.addMotif(f"BFS sz={sz} seed=12 nodes={nnodes} threads={threads_per_rank} msg_model={msg_model} exec_model={exec_model}")

    elif version == "trace":
        msg_model  = f'models/trace/bfs_msgtrace_{nnodes}-{nnodes}-{threads_per_rank}-{sz}-0.txt'
        exec_model = f'models/trace/bfs_exectrace_{nnodes}-{nnodes}-{threads_per_rank}-{sz}-0.txt'
        ep.addMotif(f"BFS sz={sz} seed=12 nodes={nnodes} threads={threads_per_rank} msg_model={msg_model} exec_model={exec_model}")

    else:
        print("ERROR: Version not recognized.")
        sys.exit(1)

    ep.addMotif("Fini")

    system = System()
    system.setTopology(topo)
    system.allocateNodes(ep,"linear")
    system.build()

