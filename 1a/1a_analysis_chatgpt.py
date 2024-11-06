import dpkt
import socket

pcap_files = ['./HW1_1.pcap', './HW1_2.pcap', './HW1_3.pcap', './HW1_4.pcap', './HW1_5.pcap', './HW1_6.pcap']

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

class Count:
    def __init__(self):
        self.dict = {}
        for port in port_dictionary:
            self.dict[port_dictionary[port]] = 0
        self.dict["ICMPv6"] = 0
        self.dict["ARP"] = 0
        self.dict["ESP"] = 0  # Add ESP counter

    def add_ports(self, src_port, dest_port):
        if src_port in port_dictionary:
            self.dict[port_dictionary[src_port]] += 1
        elif dest_port in port_dictionary:
            self.dict[port_dictionary[dest_port]] += 1

    def add(self, key):
        if key in self.dict:
            self.dict[key] += 1

for filename in pcap_files:
    with open(filename, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        count = Count()
        browsers = {}

        for timestamp, packet_data in pcap:
            try:
                eth = dpkt.ethernet.Ethernet(packet_data)
                
                if isinstance(eth.data, dpkt.ip.IP):
                    ip = eth.data
                    # Check for ESP protocol (50)
                    if ip.p == 50:
                        count.add("ESP")
                        print(f"ESP Packet: {timestamp} - {socket.inet_ntoa(ip.src)} -> {socket.inet_ntoa(ip.dst)}")
                    
                    elif isinstance(ip.data, dpkt.tcp.TCP) or isinstance(ip.data, dpkt.udp.UDP):
                        count.add_ports(ip.data.sport, ip.data.dport)
                        
                        try:
                            tcp = ip.data
                            http = dpkt.http.Request(tcp.data)  # Parse HTTP request
                            user_agent = http.headers.get('user-agent')
                            if user_agent:
                                browsers[user_agent] = True
                        except (dpkt.dpkt.NeedData, dpkt.dpkt.UnpackError):
                            continue

                elif isinstance(eth.data, dpkt.ip6.IP6):
                    ip6 = eth.data
                    if ip6.nxt == 50:  # Check for ESP protocol in IPv6
                        count.add("ESP")
                        src = socket.inet_ntop(socket.AF_INET6, ip6.src)
                        dst = socket.inet_ntop(socket.AF_INET6, ip6.dst)
                        print(f"ESP Packet: {timestamp} - {src} -> {dst}")
                    elif isinstance(ip6.data, dpkt.icmp6.ICMP6):
                        count.add("ICMPv6")
                    elif isinstance(ip6.data, dpkt.udp.UDP) or isinstance(ip6.data, dpkt.tcp.TCP):
                        count.add_ports(ip6.data.sport, ip6.data.dport)

                elif isinstance(eth.data, dpkt.arp.ARP):
                    count.add("ARP")

            except Exception as e:
                print("Exception occurred:", e)

        # Summary output
        print(f"File {filename}")
        for key, value in count.dict.items():
            if value > 0:
                print(f"{key.ljust(7)}: {value}")
        for key in browsers:
            print("Browser:", key)
        print()
