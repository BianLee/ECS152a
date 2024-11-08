import dpkt
import socket

pcap_files = ['./HW1_1.pcap', './HW1_2.pcap', './HW1_3.pcap', './HW1_4.pcap', './HW1_5.pcap', './HW1_6.pcap']

# define the dictionary so that it forms tkhe key : value pair of port number : protocol name
port_dictionary = {
    80: "HTTP",
    443: "HTTPS",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    110: "POP",
    53: "DNS",
    4500: "ESP",
    5353: "MDNS",
    1900: "SSDP"
}

# define the ports in a python dictionary
application_protocols = {
    "HTTP": True, "HTTPS": True, "FTP": True,
    "Telnet": True, "SMTP": True, "POP": True,
    "mDNS": True, "SSDP": True,
}

class Count:
    def __init__(self):
        self.dict = {} 

        for port in port_dictionary:
            self.dict[port_dictionary[port]] = 0
        self.dict["ICMPv6"] = 0 #add additional fields for other protocls like ICMP and ARP
        self.dict["ARP"] = 0

    def add_ports(self, src_port, dest_port):
        if (src_port in port_dictionary):
            self.dict[port_dictionary[src_port]]+=1
        elif (dest_port in port_dictionary): 
            self.dict[port_dictionary[dest_port]]+=1

    def add(self, key):
        if key in self.dict:
            self.dict[key] += 1

for i in range(len(pcap_files)): # analyze all 6 by interating through

    filename = pcap_files[i]
    f = open(filename, 'rb') # open binary mode, if not there is error
    pcap = dpkt.pcap.Reader(f)
    count = Count()
    browsers = {}

    for timestamp, packet_data in pcap:
        try:
            eth = dpkt.ethernet.Ethernet(packet_data)
            
            if isinstance(eth.data, dpkt.ip.IP):
                ip = eth.data
                if isinstance(ip.data, dpkt.tcp.TCP) or isinstance(ip.data, dpkt.udp.UDP):

                    if len(tcp.data) == 0: # skipping over the packets with no application layer data
                        continue


                    count.add_ports(ip.data.sport, ip.data.dport)

                    try:
                        tcp = ip.data
                        http = dpkt.http.Request(tcp.data) # Parse HTTP request
                        user_agent = http.headers.get('user-agent')
                        browsers[user_agent] = True
                    except (dpkt.dpkt.NeedData, dpkt.dpkt.UnpackError):
                        continue
                        
            elif isinstance(eth.data, dpkt.ip6.IP6):
                ip6 = eth.data
                if ip6.nxt == 50: #ESP for activity #6 (over SSH)
                    count.add("ESP")
                    src = socket.inet_ntop(socket.AF_INET6, ip6.src)
                    dst = socket.inet_ntop(socket.AF_INET6, ip6.dst)

                    print("ESP packet: ", timestamp)
                    # print(f"ESP Packet: {timestamp} - {src} -> {dst}")

                if isinstance(ip6.data, dpkt.icmp6.ICMP6):
                    count.add("ICMPv6")
                elif isinstance(ip6.data, dpkt.udp.UDP) or isinstance(ip6.data, dpkt.tcp.TCP):
                    count.add_ports(ip6.data.sport, ip6.data.dport)
                
            elif isinstance(eth.data, dpkt.arp.ARP):
                count.add("ARP")
        except:
            print("exception block, error")

                    

    print(f"File {filename}")
    for key in count.dict:
        if key in application_protocols and count.dict[key] > 0:
            print(f"{key.ljust(7)}: {count.dict[key]}")  
    for key in browsers:
        print("Browser: ", key)
    print()
            


for i in range(len(pcap_files)): # analyze all 6

    filename = pcap_files[i]
    f = open(filename, 'rb') # open binary mode, if not there is error
    pcap = dpkt.pcap.Reader(f)
    
    print(f"File {filename}")
    print("Timestamp           :   source -> destination")
    
    for timestamp, packet_data in pcap:
        
        eth = dpkt.ethernet.Ethernet(packet_data)

        src = None
        dst = None 
        
        # only check ipv4
      
        '''
        if isinstance(eth.data, dpkt.ip6.IP6):
            ip6 = eth.data
            src = socket.inet_ntop(socket.AF_INET6, ip6.src)
            dst = socket.inet_ntop(socket.AF_INET6, ip6.dst)
        '''
        

        if isinstance(eth.data, dpkt.ip.IP):
            ip = eth.data
            src = socket.inet_ntoa(ip.src)
            dst = socket.inet_ntoa(ip.dst)

        if src != None and dst != None: 
            print(f"{timestamp}".ljust(20) + f":   {str(src).ljust(38)} -> {dst}")

    print()
    print()

