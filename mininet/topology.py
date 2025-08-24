#!/usr/bin/env python3
"""
Mininet Topology for ACNI Project
DASH Video Streaming with Edge Computing and SDN
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, OVSController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

class ACNITopology(Topo):
    """Custom topology for ACNI project"""
    
    def build(self):
        # Add switches
        central_switch = self.addSwitch('s1')
        edge_switch = self.addSwitch('s2')
        
        # Add hosts with shorter names
        # Central server
        central_server = self.addHost('h1', ip='10.0.1.10/24')
        
        # Edge server
        edge_server = self.addHost('h2', ip='10.0.2.10/24')
        
        # Client hosts
        client1 = self.addHost('h3', ip='10.0.2.20/24')
        client2 = self.addHost('h4', ip='10.0.2.21/24')
        client3 = self.addHost('h5', ip='10.0.2.22/24')
        
        # Add links
        # Connect servers to switches
        self.addLink(central_server, central_switch, bw=100)  # 100 Mbps
        self.addLink(edge_server, edge_switch, bw=50)         # 50 Mbps
        
        # Connect clients to edge switch
        self.addLink(client1, edge_switch, bw=10)             # 10 Mbps
        self.addLink(client2, edge_switch, bw=10)             # 10 Mbps  
        self.addLink(client3, edge_switch, bw=10)             # 10 Mbps
        
        # Bottleneck link between switches (simulating WAN)
        self.addLink(central_switch, edge_switch, bw=20, delay='50ms')  # 20 Mbps, 50ms delay

def run_topology():
    """Run the topology with default controller"""
    topo = ACNITopology()
    
    # Use default controller for now (no SDN)
    net = Mininet(topo=topo, 
                  controller=OVSController,
                  link=TCLink,
                  autoSetMacs=True)
    
    print("Starting network...")
    net.start()
    
    print("Network topology created!")
    print("Central Server (h1): 10.0.1.10")
    print("Edge Server (h2): 10.0.2.10") 
    print("Clients: h3-h5 (10.0.2.20-22)")
    print("\nTesting connectivity...")
    
    # Test basic connectivity
    net.pingAll()
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_topology()
