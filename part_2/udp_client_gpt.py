import socket

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5500

string = '0'*1024 # 1KB of data


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect((SERVER_HOST, SERVER_PORT))

    num_packets = 1024*100  # Total number of 1KB chunks to send

    for _ in range(num_packets):
        s.sendall(string.encode('utf-8'))

    # Send end signal to server
    s.sendall(b"END")

    # Receive throughput result from server
    data, _ = s.recvfrom(1024)
    throughput = float(data.decode())

print(f"The throughput is {round(throughput/1024**2)}mb/s from {SERVER_HOST}:{SERVER_PORT}")
