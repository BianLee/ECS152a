import socket

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5500

large_string = '0'*100*1024**2


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((SERVER_HOST, SERVER_PORT))
    s.sendall(large_string.encode('utf-8'))
    data = s.recv(1024)

through_put = float(data.decode())
print(f"The throughput is {round(through_put/1024**2)}mb/s from {SERVER_HOST}:{SERVER_PORT}")
