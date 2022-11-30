#!/usr/bin/env python
#
# Copyright 2009-2020 NTESS. Under the terms
# of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# Copyright (c) 2009-2020, NTESS
# All rights reserved.
#
# This file is part of the SST software package. For license
# information, see the LICENSE file in the top level directory of the
# distribution.
import sst
import sys
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

    # Create an "empty" job of the remaining ranks.
    #empty_job = EmptyJob(num_jobs + 1, rem_ranks)

    if (len(sys.argv) < 4):
        print("Too few args")
        print("--model-options=\"<nodes> <threads_per_rank> <scale>\"")
        sys.exit(1)

    nnodes = int(sys.argv[1])
    threads_per_rank = int(sys.argv[2])
    sz = int(sys.argv[3])

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

    # define the motifs to run
    ep.addMotif("Init")
    #ep.addMotif("BFS sz={} seed=12 nodes={} threads=4 comm_model=msg_size.model comp_model=exec_time.model".format(sz, nnodes))
    ep.addMotif(f"BFS sz={sz} seed=12 nodes={nnodes} threads={threads_per_rank} msg_model=msg_size_2D.model exec_model=exec_time_2D.model")

    #ep.addMotif("Allreduce")
    ep.addMotif("Fini")

    # Allocate jobs to system

    # First, randomly allocate the empty job (this will spread out the
    # other jobs across the whole machine
    #system.allocateNodes(empty_job,"random",15)

    system = System()
    system.setTopology(topo)

    system.allocateNodes(ep,"linear")

    system.build()

    #sst.enableStatisticsForComponentType("merlin.linkcontrol",["send_bit_count","recv_bit_count"],{"type":"sst.AccumulatorStatistic","rate":"20us"},False)
    #sst.enableStatisticsForComponentType("merlin.hr_router",["send_bit_count"],{"type":"sst.AccumulatorStatistic","rate":"0us"},False)
    #sst.setStatisticLoadLevel(9)

    #sst.setStatisticOutput("sst.statOutputCSV");
    #sst.setStatisticOutputOptions({
    #    "filepath" : "output/stats" + suffix + ".csv",
    #    "separator" : ", "
    #})

