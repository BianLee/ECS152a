import dpkt

def analyze_pcap_activity(pcap_file):
    activities = []
    with open(pcap_file, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        
        for timestamp, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            if isinstance(eth.data, dpkt.ip.IP):
                ip = eth.data
                src_ip = f"{ip.src[0]}.{ip.src[1]}.{ip.src[2]}.{ip.src[3]}"
                dst_ip = f"{ip.dst[0]}.{ip.dst[1]}.{ip.dst[2]}.{ip.dst[3]}"
                
                if isinstance(ip.data, dpkt.tcp.TCP):
                    tcp = ip.data
                    payload = tcp.data.decode('utf-8', errors='ignore')
                    activities.append((src_ip, dst_ip, len(payload), payload[:50]))  # Log only first 50 chars

    return activities

# Compare activities between two files
def compare_activities(file1, file2):
    activities1 = analyze_pcap_activity(file1)
    activities2 = analyze_pcap_activity(file2)
    
    differences = []
    for i, (act1, act2) in enumerate(zip(activities1, activities2)):
        if act1 != act2:
            differences.append((i, act1, act2))
            
    return differences

# Analyze and compare
differences = compare_activities('ass1_2.pcap', 'ass1_3.pcap')
for i, act1, act2 in differences:
    print(f"Difference at packet {i}:")
    print(f"File 1: {act1}")
    print(f"File 2: {act2}")
