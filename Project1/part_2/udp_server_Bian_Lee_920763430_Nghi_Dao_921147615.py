import socket
import time

HOST = '127.0.0.1'
PORT = 5500


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
    server_socket.bind((HOST, PORT))
    
    # Prepare to receive data
    total_data_received = 0
    start_time = None
    
    while True:
        try:
            data, client_address = server_socket.recvfrom(1024)  # Receive data in chunks of 1KB
            if start_time == None:
                start_time = time.time()
            if data == b"END":  # Signal to end transmission
                break
            total_data_received += len(data)
        except socket.timeout:
            print("Time out")
            break
        except socket.error as e:
            print(f"Socket error: {e}")
            break
    
    end_time = time.time()
    if start_time:
        time_taken = end_time - start_time
        throughput = total_data_received / time_taken 
        
        print(f"Total data received: {total_data_received / (1000*1000):.2f} MB")
        print(f"Time taken: {time_taken} seconds")
        print(f"Throughput: {round(throughput/1000)} KB/s")
        
        # Send throughput result back to client
        server_socket.sendto(str(throughput).encode("utf-8"), client_address)
    else:
        print("No packets received")