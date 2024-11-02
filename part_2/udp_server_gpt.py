import socket
import time

HOST = '127.0.0.1'
PORT = 5500


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
    server_socket.bind((HOST, PORT))
    
    # Prepare to receive data
    total_data_received = 0
    start_time = time.time()
    
    while True:
        data, client_address = server_socket.recvfrom(1024)  # Receive data in chunks of 1KB
        if data == b"END":  # Signal to end transmission
            break
        total_data_received += len(data)
    
    end_time = time.time()
    time_taken = end_time - start_time
    throughput = total_data_received / time_taken 
    
    print(f"Total data received: {total_data_received / (1024*1024):.2f} MB")
    print(f"Time taken: {time_taken} seconds")
    print(f"Throughput: {round(throughput/1000)} Mbs")
    
    # Send throughput result back to client
    server_socket.sendto(str(throughput).encode("utf-8"), client_address)
    server_socket.close()
