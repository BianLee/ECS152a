import socket

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5500

string = '0'*1000 # 1KB of data


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect((SERVER_HOST, SERVER_PORT))

    num_packets = 1000*100  # Total number of 1KB chunks to send

    for i in range(num_packets):
        try:
            s.sendto(string.encode("utf-8"), (SERVER_HOST, SERVER_PORT))
        except socket.error as e:
            print(f"Error sending packet {i}: {e}")
            continue

    # Send end signal to server
    
    for i in range(5):
        try:
            s.sendto(b"END", (SERVER_HOST, SERVER_PORT))
            # Receive throughput result from server
            data, _ = s.recvfrom(1024)
            throughput = float(data.decode())
            print(f"The throughput is {round(throughput/1000)}KB/s from {SERVER_HOST}:{SERVER_PORT}")
            break
        except socket.timeout:
            print("Time out")
            continue
        except socket.error as e:
            print(f"Socket error: {e}")
            continue