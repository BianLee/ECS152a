import dpkt

def extract_secrets_from_pcap(pcap_file):
    secrets = []
    with open(pcap_file, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        
        for timestamp, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            if isinstance(eth.data, dpkt.ip.IP):
                ip = eth.data
                if isinstance(ip.data, dpkt.tcp.TCP):
                    tcp = ip.data
                    if tcp.dport == 80 or tcp.sport == 80:  # Port 80 for HTTP traffic
                        try:
                            http = dpkt.http.Request(tcp.data)
                            if b"secret" in tcp.data.lower():
                                secret_info = tcp.data.decode('utf-8', errors='ignore')
                                secrets.append(secret_info)
                                print(f"Secret found: {secret_info}")
                        except (dpkt.dpkt.UnpackError, UnicodeDecodeError):
                            continue
    return secrets

# Run the function
secrets = extract_secrets_from_pcap('ass1_1.pcap')
for secret in secrets:
    print(secret)
