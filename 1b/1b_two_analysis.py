import dpkt
import socket


ass1_2 = dpkt.pcap.Reader(open("ass1_2.pcap", 'rb'))
ass1_3 = dpkt.pcap.Reader(open("ass1_3.pcap", 'rb'))


def get_location(ip):
    url = f"https://ipinfo.io/{str(ip)}/json"
    response = requests.get(url).json()
    if "city" in response:
        return response["city"]
    return "Unknown"
    
def display(f):
    initial = None
    for timestamp, packet_data in f:
        if initial == None:
            initial = timestamp
        
        eth = dpkt.ethernet.Ethernet(packet_data)
        
        if isinstance(eth.data, dpkt.ip.IP):
            ip = eth.data
            if ip.p == dpkt.ip.IP_PROTO_ICMP:
                icmp = ip.data
                out = f"{timestamp-initial:.4f}".ljust(8)+ f" | ICMP | {socket.inet_ntoa(ip.src).ljust(15)} ->   {socket.inet_ntoa(ip.dst)}"
                out += f" | {get_location(socket.inet_ntoa(ip.src)).ljust(12)}"
                if icmp.type == 11:
                    print(out + " | Time Exceeded")
                elif icmp.type == 3:
                    print(out + " | Protocol Unreachable")
                else:
                    print(out)
            else:
                print("Non ICMP packet")

display(ass1_2)
print()
print()
display(ass1_3)


            