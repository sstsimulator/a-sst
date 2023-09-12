import sst
from sst.merlin.base import *
from sst.firefly import *

from sst.merlin.topology import topoDragonFly

platdef = PlatformDefinition.compose("perlmutter",[("firefly-defaults","ALL")])

platdef.addParamSet("router",{
    "link_bw" : "200Gb/s",
    "flit_size" : "16B",
    "xbar_bw" : "250Gb/s",
    "input_latency" : "50ns",
    "output_latency" : "50ns",
    "input_buf_size" : "16kB",
    "output_buf_size" : "16kB",

    # Set up the number of VNs to use; using 2 since one of the jobs
    # remaps to VN 1
    # "num_vns" : 2,
    # Optionally set up the QOS
    #"qos_settings" : [50,50]

    # Set up the arbitration type for the routers
    # "xbar_arb" : "merlin.xbar_arb_lru",
})

platdef.addParamSet("firefly.basic_nic", {
    "nic2host_lat" : "350ns",
    "rxMatchDelay_ns" : 350,
    "txDelay_ns" : 350,
    "hostReadDelay_ns" : 350,
    "packetSize" : "2048B",
    "packetOverhead" : 0,

    "numVNs" : 1, # total number of VN used
    "getHdrVN" : 0, # VN used for sending a get request
    "getRespSmallVN" : 0, # VN used for sending a get response <= getRespSize
    "getRespLargeVN" : 0, # VN used for sending a get response > getRespSize
    "getRespSize" : 15000,
})


platdef.addParamSet("firefly.functionsm",{
    'verboseLevel': 0,
    'defaultReturnLatency': 50000,
    'defaultEnterLatency': 50000,

    'defaultModule': 'firefly',
    'smallCollectiveVN' : 0, # VN used for collectives <= smallCollectiveSize
    'smallCollectiveSize' : 8,
})

# ctrlMsg = {
#
#     'pqs.verboseMask': -1,
#     'pqs.verboseLevel': 0,
# }
#
# platdef.addParamSet("firefly.ctrlMsgProto", ctrlMsg)
# platdef.addParamSet("firefly.ctrlMsg", ctrlMsg)

platdef.addParamSet("firefly.ctrl", {
    'sendStateDelay_ps' : 200,
    'recvStateDelay_ps' : 200,
    'waitallStateDelay_ps' : 200,
    'waitanyStateDelay_ps' : 20000,
    
    'pqs.verboseMask': 1,
    'pqs.verboseLevel': 10,



    'verboseLevel': 0,

    'sendAckDelay_ns': 50,
    'matchDelay_ns': 50,

    'shortMsgLength': 8191,

    'regRegionXoverLength': 4096,
    'regRegionBaseDelay_ns': 0,
    'regRegionPerPageDelay_ns': 0,
    
    'rendezvousVN' : 0, # VN used to send a match header that requires a get by the target
    'ackVN' : 0,  # VN used to send an ACK back to originator after target does a get

    'txMemcpyMod': 'firefly.LatencyMod',
    "txMemcpyModParams.op" : "Mult", # this is the base latency for a memcpy, the following are added to this
    "txMemcpyModParams.base" : "10ns", # this is the base latency for a memcpy, the following are added to this
    'txMemcpyModParams.range.0': '0-255:175ps',
    'txMemcpyModParams.range.1': '256-8191:250ps',
    'txMemcpyModParams.range.2': '8192-:100ps',
    
    'rxMemcpyMod': 'firefly.LatencyMod',
    'rxMemcpyModParams.op': 'Mult',
    'rxMemcpyModParams.base': "10ns",
    'rxMemcpyModParams.range.0': '0-:1ps',

    'txSetupMod': 'firefly.LatencyMod',
    'txSetupModParams.base': '10ns',

    'rxSetupMod': 'firefly.LatencyMod',
    'rxSetupModParams.base': '10ns',


    'txFiniMod': 'firefly.LatencyMod',
    # 'txFiniModParams.op': 'Mult',
    'txFiniModParams.base': '10ns',

    'rxFiniMod': 'firefly.LatencyMod',
    # 'rxFiniModParams.op': 'Mult',
    'rxFiniModParams.base': '10ns',

    'rxPostMod': 'firefly.LatencyMod',
    'rxPostModParams.op': 'Mult',
    'rxPostModParams.base': '10ns',
    'rxPostModParams.range.0': '0-255:100ps',
    'rxPostModParams.range.1': '256-8191:50ps',
    'rxPostModParams.range.2': '8192-:75ps',    


})


platdef.addParamSet("network_interface",{
    "link_bw" : "200Gb/s",
    "input_buf_size" : "16kB",
    "output_buf_size" : "16kB"
})

platdef.addClassType("network_interface","sst.merlin.interface.ReorderLinkControl")


class PerlmutterSystem(System):
    def __init__(self):
        System.__init__(self);

        # Initialize the topology

        topo = topoDragonFly()
        topo.hosts_per_router = 16
        topo.routers_per_group = 16
        topo.intragroup_links = 2
        topo.intergroup_links = 4
        topo.num_groups = 19
        topo.link_latency = "100ns"
        topo.host_link_latency = "50ns"
        topo.algorithm = "ugal"

        group_size = topo.hosts_per_router * topo.routers_per_group
        
        self.setTopology(topo, 1)
        
        # allocate to the nodes that represent GPU nodes (7 groups worth)
        block = EmptyJob(-2, group_size * 7)
        block.network_interface = self.topology.router.getDefaultNetworkInterface()
        block.network_interface.link_bw = "1 GB/s"
        self.allocateNodes(block,"linear");


    def getNumRemainingNodes(self):
        return len(self._available_nodes)
