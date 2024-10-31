import dpkt

filename='./HW1_1.pcap'
f = open(filename, 'rb')
pcap = dpkt.pcap.Reader(f)

for timestamp, packet_data in pcap:
    eth = dpkt.ethernet.Ethernet(packet_data)
    ip = eth.data 
    print(ip) # right now everything is in binary