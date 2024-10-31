import dpkt

filename='./HW1_1.pcap'
f = open(filename, 'rb')
pcap = dpkt.pcap.Reader(f)