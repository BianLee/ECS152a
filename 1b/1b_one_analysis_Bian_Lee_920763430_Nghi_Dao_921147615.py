import dpkt
import json

filename = "ass1_1.pcap"


with open(filename, 'rb') as f:
    pcap = dpkt.pcap.Reader(f)

    for timestamp, packet_data in pcap:
        
        try:
            eth = dpkt.ethernet.Ethernet(packet_data)

            # Check if the packet is an IP packet
            if isinstance(eth.data, dpkt.ip6.IP6):
                
                ip = eth.data 
                if isinstance(ip.data, (dpkt.tcp.TCP, dpkt.udp.UDP)):
                    tcp = ip.data
                    payload = tcp.data
                    for line in payload.decode().split("\n"):   
                        if "secret" in line or "password" in line:
                            print(line)

        
        except Exception as e:
            continue