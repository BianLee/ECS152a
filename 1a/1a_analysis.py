import dpkt

filename='./HW1_1.pcap'
f = open(filename, 'rb') #open binary mode, if not there is error
pcap = dpkt.pcap.Reader(f)



#define the mapping of port number : protocol
port_dictionary = {
    80: "HTTP",
    443: "HTTPS",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    110: "POP",
    53: "DNS",
}

count_dictionary = dict()
for key, value in port_dictionary.items(): #initializing all the protocol count to 0 first
    count_dictionary[key] = 0

for timestamp, packet_data in pcap:
    try:
        eth = dpkt.ethernet.Ethernet(packet_data)
        if isinstance(eth.data, dpkt.ip.IP): # case where it's an IP packet
            ip = eth.data

            if isinstance(ip.data, dpkt.tcp.TCP): # if TCP
                tcp = ip.data
                if (tcp.sport in port_dictionary): #tcp.sport is source
                    count_dictionary[tcp.sport]+=1
                elif (tcp.dport in port_dictionary): #tcp.dport is destination
                    count_dictionary[tcp.dport]+=1
    except:
        print("exception block, error")


print(count_dictionary)

