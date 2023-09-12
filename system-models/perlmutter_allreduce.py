#!/usr/bin/env python
#
# Copyright 2009-2022 NTESS. Under the terms
# of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# Copyright (c) 2009-2022, NTESS
# All rights reserved.
#
# This file is part of the SST software package. For license
# information, see the LICENSE file in the top level directory of the
# distribution.

import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *

from sst.ember import *

if __name__ == "__main__":

    module = PlatformDefinition.loadPlatformFile("perlmutter_platform")
    PlatformDefinition.setCurrentPlatform("perlmutter")

    # Allocate the Perlmutter system. This will create the topology
    # since it's set up in the platform file
    system = module.PerlmutterSystem()

    # Allocate all the remaining nodes in the system (the Perlmutter
    # system blocks off all the GPU nodes, so use
    # system.getNumRemainingNodes() instead of
    # system.topo.getNumNodes()
    ep = EmberMPIJob(0,system.getNumRemainingNodes())
    ep.addMotif("Init")
    ep.addMotif("Allreduce")
    ep.addMotif("Fini")
    ep.nic.nic2host_lat= "100ns"

    system.allocateNodes(ep, "linear")
    
    system.build()

    # sst.setStatisticLoadLevel(9)

    # sst.setStatisticOutput("sst.statOutputCSV");
    # sst.setStatisticOutputOptions({
    #     "filepath" : "stats.csv",
    #     "separator" : ", "
    # })

