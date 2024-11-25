import socket
import struct
import time

# Predefined root DNS server IPs
ROOT_DNS_SERVERS = ["198.41.0.4", "199.9.14.201", "192.33.4.12", "199.7.91.13"]

def create_dns_query(domain, query_type=1):
    """Construct a DNS query packet."""
    transaction_id = b'\xaa\xaa'  # Unique ID
    flags = b'\x01\x00'          # Standard query with recursion desired
    questions = b'\x00\x01'      # One question
    answer_rrs = b'\x00\x00'
    authority_rrs = b'\x00\x00'
    additional_rrs = b'\x00\x00'

    # Encode domain name into DNS format
    query = b''
    for part in domain.split('.'):
        query += struct.pack('!B', len(part)) + part.encode()
    query += b'\x00'  # End of domain name
    query_type = struct.pack('!H', query_type)  # Query type (1 for A records)
    query_class = b'\x00\x01'  # Class IN

    return (
        transaction_id
        + flags
        + questions
        + answer_rrs
        + authority_rrs
        + additional_rrs
        + query
        + query_type
        + query_class
    )

def parse_dns_response(response):
    """Parse DNS response to extract IP addresses or referral servers."""
    header = response[:12]
    transaction_id, flags, questions, answer_rrs, authority_rrs, additional_rrs = struct.unpack('!6H', header)

    # Skip question section
    offset = response.find(b'\x00') + 5  # Domain name + null terminator + type and class
    records = response[offset:]

    # Parse answer, authority, and additional sections
    ips = []
    for _ in range(answer_rrs + authority_rrs + additional_rrs):
        record_type = struct.unpack('!H', records[2:4])[0]
        data_length = struct.unpack('!H', records[10:12])[0]
        if record_type == 1:  # Type A (IPv4 address)
            ip = socket.inet_ntoa(records[12:12 + data_length])
            ips.append(ip)
        records = records[12 + data_length:]  # Move to the next record
    return ips

def iterative_dns_resolution(domain):
    """Perform iterative DNS resolution."""
    current_servers = ROOT_DNS_SERVERS
    while True:
        for server in current_servers:
            try:
                # Create a socket and send DNS query
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.settimeout(5)
                    query = create_dns_query(domain)
                    start_time = time.time()
                    s.sendto(query, (server, 53))
                    response, _ = s.recvfrom(512)
                    rtt = time.time() - start_time

                    print(f"Query to {server} succeeded in {rtt:.2f} seconds")

                    # Parse the response to get answers or referrals
                    ips = parse_dns_response(response)
                    if ips:  # If we get an IP, resolution is complete
                        return ips

                    # Extract referral servers (e.g., TLD or authoritative servers)
                    current_servers = parse_referral_servers(response)
                    break  # Move to the next iteration with new servers
            except socket.timeout:
                print(f"Query to {server} timed out. Trying next server...")
        else:
            raise Exception("Failed to resolve domain.")

def parse_referral_servers(response):
    """Extract referral DNS server IPs from authority or additional sections."""
    # This function would parse the authority and additional sections
    # to get IP addresses of the next set of DNS servers.
    # For simplicity, we'll assume that root or TLD servers provide necessary referrals.
    return []  # Implement as needed

def main():
    domain = "tmz.com"

    print(f"Resolving {domain} iteratively...")
    try:
        ips = iterative_dns_resolution(domain)
        print(f"Resolved IPs for {domain}: {ips}")

        # Test HTTP connection to the resolved IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ips[0], 80))
            s.sendall(b"GET / HTTP/1.1\r\nHost: tmz.com\r\nConnection: close\r\n\r\n")
            response = s.recv(1024)
            print(f"Received HTTP response: {response[:100]}...")
    except Exception as e:
        print(f"Failed to resolve domain: {e}")

if __name__ == "__main__":
    main()