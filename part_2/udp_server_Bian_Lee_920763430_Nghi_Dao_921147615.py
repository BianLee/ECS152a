import socket
import time

HOST = '127.0.0.1'
PORT = 5500


packet_size = 1024**2 * 100

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
     server_socket.bind((HOST, PORT))
     server_socket.listen()
     
     client_socket, (client_addr, client_port) = server_socket.accept()
     start_time = time.time()
     data = client_socket.recv(packet_size)
     end_time = time.time()

     through_put = packet_size/(end_time - start_time)
     client_socket.sendall(str(through_put).encode('utf-8'))