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
from sst.merlin.topology import *
from sst.merlin.interface import *
from sst.merlin.router import *

if __name__ == "__main__":

    module = PlatformDefinition.loadPlatformFile("perlmutter_platform")
    PlatformDefinition.setCurrentPlatform("perlmutter")

    # Allocate the system. This will create the topology since it's
    # set up in the platform file
    system = module.PerlmutterSystem()

    ### set up the endpoint
    #vep = TestJob(0,system.getNumRemainingNodes())
    ep = TestJob(0,128)
        
    system.allocateNodes(ep,"random")

    system.build()
    

    # sst.setStatisticLoadLevel(9)

    # sst.setStatisticOutput("sst.statOutputCSV");
    # sst.setStatisticOutputOptions({
    #     "filepath" : "stats.csv",
    #     "separator" : ", "
    # })

