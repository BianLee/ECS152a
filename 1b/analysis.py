import dpkt

filename='./ass1_1.pcap'
file = open(filename)
pcap = dpkt.pcap.Reader(file)