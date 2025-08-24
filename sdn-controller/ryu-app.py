#!/usr/bin/env python3
"""
Ryu SDN Controller Application for ACNI Project
Video Traffic Management and Monitoring
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types, ipv4, tcp
import time

class ACNIController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ACNIController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.datapaths = {}
        
        # Server IPs
        self.central_server = '10.0.1.10'
        self.edge_server = '10.0.2.10'
        
        # Traffic monitoring
        self.traffic_stats = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Handle switch connection"""
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        self.datapaths[datapath.id] = datapath
        self.logger.info(f"Switch connected: {datapath.id}")

        # Install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        """Add a flow entry to switch"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """Handle incoming packets"""
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        self.mac_to_port.setdefault(dpid, {})

        # Learn MAC address
        self.mac_to_port[dpid][src] = in_port

        # Decide output port
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Install flow if we know the destination
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(datapath, 1, match, actions)

        # Handle video traffic redirection logic here
        self.handle_video_traffic(pkt, datapath, in_port, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def handle_video_traffic(self, pkt, datapath, in_port, actions):
        """Handle video streaming traffic redirection"""
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        if ipv4_pkt:
            tcp_pkt = pkt.get_protocol(tcp.tcp)
            if tcp_pkt and tcp_pkt.dst_port == 80:
                # Log traffic for monitoring
                self.log_traffic_stats(ipv4_pkt.src, ipv4_pkt.dst)
                
                # Add higher priority flows for video traffic
                parser = datapath.ofproto_parser
                match = parser.OFPMatch(
                    eth_type=ether_types.ETH_TYPE_IP,
                    ipv4_dst=ipv4_pkt.dst,
                    ip_proto=6,  # TCP
                    tcp_dst=80
                )
                self.add_flow(datapath, 10, match, actions)  # Higher priority
                
                self.logger.info(f"Video traffic from {ipv4_pkt.src} to {ipv4_pkt.dst}")

    def log_traffic_stats(self, src, dst):
        """Log traffic statistics for analysis"""
        timestamp = time.time()
        key = f"{src}->{dst}"
        
        if key not in self.traffic_stats:
            self.traffic_stats[key] = []
        
        self.traffic_stats[key].append(timestamp)

    def redirect_to_edge_server(self, datapath, ipv4_pkt, tcp_pkt, in_port):
        """Redirect traffic to edge server based on conditions"""
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        
        # Check if destination is central server and redirect to edge
        if ipv4_pkt.dst == self.central_server:
            # Modify destination IP to edge server
            actions = [
                parser.OFPActionSetField(ipv4_dst=self.edge_server),
                parser.OFPActionOutput(self.get_port_to_edge_server(datapath.id))
            ]
            
            match = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=ipv4_pkt.src,
                ipv4_dst=self.central_server,
                ip_proto=6,
                tcp_dst=80
            )
            
            self.add_flow(datapath, 20, match, actions)
            self.logger.info(f"Redirected {ipv4_pkt.src} from central to edge server")

    def request_stats(self):
        """Request flow statistics from switches"""
        for dp in self.datapaths.values():
            parser = dp.ofproto_parser
            req = parser.OFPFlowStatsRequest(dp)
            dp.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        """Handle flow statistics reply"""
        flows = []
        for stat in ev.msg.body:
            flows.append({
                'table_id': stat.table_id,
                'match': stat.match,
                'packet_count': stat.packet_count,
                'byte_count': stat.byte_count
            })
        
        # Log or save stats for analysis
        self.logger.info(f"Flow stats: {len(flows)} flows")
