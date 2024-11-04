import dpkt
import socket

pcap_files = ['./HW1_1.pcap', './HW1_2.pcap', './HW1_3.pcap', './HW1_4.pcap', './HW1_5.pcap', './HW1_6.pcap']

for i in range(len(pcap_files)): #analyze all 6


    filename = pcap_files[i]
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
                
                elif isinstance(ip.data, dpkt.udp.UDP):
                    # print("hello")
                    udp = ip.data
              
                    if (udp.sport in port_dictionary): #udp.sport is source
                        # print('asdffsdaf')
                        count_dictionary[udp.sport]+=1
                    elif (udp.dport in port_dictionary): #udp.dport is destination
                        # print('asdffsdaf')
                        count_dictionary[udp.dport]+=1
                
            elif isinstance(eth.data, dpkt.ip6.IP6):
                ip6 = eth.data

                if isinstance(ip6.data, dpkt.icmp6.ICMP6):
                    if ("ICMPv6" not in count_dictionary):
                        count_dictionary["ICMPv6"] = 1 #if it doesn't exist just initialize
                    else:
                        count_dictionary["ICMPv6"] += 1
                
                elif isinstance(ip6.data, dpkt.udp.UDP):
                    udp = ip6.data
                    if (udp.sport in port_dictionary):
                        count_dictionary[udp.sport] += 1
                    elif (udp.dport in port_dictionary): #should this be if or elif?
                        count_dictionary[udp.dport] += 1 
                
                elif isinstance(ip6.data, dpkt.tcp.TCP):
                    tcp = ip6.data
                    if (tcp.sport in port_dictionary):
                        count_dictionary[tcp.sport] += 1
                    elif (tcp.dport in port_dictionary):  #should this be if or elif?
                        count_dictionary[tcp.dport] += 1

  
                                
        except:
            print("exception block, error")


    print(pcap_files[i] + ": ")
    print(count_dictionary)
    print("\n") #for formatting


#output results
'''
./HW1_1.pcap: 
{80: 0, 443: 60, 21: 0, 22: 0, 23: 0, 25: 0, 110: 0, 53: 0}


./HW1_2.pcap: 
{80: 0, 443: 15, 21: 0, 22: 0, 23: 0, 25: 0, 110: 0, 53: 0}


./HW1_3.pcap: 
{80: 0, 443: 0, 21: 0, 22: 0, 23: 0, 25: 0, 110: 0, 53: 0}


./HW1_4.pcap: 
{80: 0, 443: 272, 21: 0, 22: 0, 23: 0, 25: 0, 110: 0, 53: 0}


./HW1_5.pcap: 
{80: 0, 443: 5, 21: 0, 22: 0, 23: 0, 25: 0, 110: 0, 53: 0}


./HW1_6.pcap: 
{80: 0, 443: 12, 21: 0, 22: 0, 23: 0, 25: 0, 110: 0, 53: 0}

'''
