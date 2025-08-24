#!/usr/bin/env python3
"""
Simple Mininet Topology for ACNI Project
DASH Video Streaming with Edge Computing
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel

class SimpleACNITopology(Topo):
    """Simple topology for ACNI project"""
    
    def build(self):
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        
        # Add hosts with simple IPs
        h1 = self.addHost('h1', ip='192.168.1.10')  # Central server
        h2 = self.addHost('h2', ip='192.168.2.10')  # Edge server
        h3 = self.addHost('h3', ip='192.168.2.20')  # Client 1
        h4 = self.addHost('h4', ip='192.168.2.21')  # Client 2
        
        # Add simple links (no bandwidth limiting for now)
        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(s1, s2)

def run_topology():
    """Run the simple topology"""
    topo = SimpleACNITopology()
    net = Mininet(topo=topo)
    
    print("Starting simple network...")
    net.start()
    
    print("Network created!")
    print("Central Server (h1): 192.168.1.10")
    print("Edge Server (h2): 192.168.2.10") 
    print("Clients: h3-h4 (192.168.2.20-21)")
    
    # Basic connectivity test
    print("\nTesting connectivity...")
    net.pingAll()
    
    print("\nStarting CLI (type 'help' for commands, 'exit' to quit)")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_topology()
