import socket
import json

data = {
    "server_ip": "127.0.0.1", # The server's IP (destination)
    "server_port": 50005, # The server's port (destination)
    "message": "ping" # The actual message
}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    # the client needs to send request to the proxy, that's why the proxy port number is specified
    client_socket.connect(("127.0.0.1", 50000)) # connect to the proxy server by specifying the proxy server port
    temp = json.dumps(data)
    client_socket.sendall(temp.encode()) #send data to proxy server

    
    response = client_socket.recv(1024).decode()
    
    print("got back the response")
    print(response)


# overall design: 
# client --> proxy --> server --> proxy --> client (unless the server_ip is on the IP block list)
# .py run order: server, proxy-server, then client 