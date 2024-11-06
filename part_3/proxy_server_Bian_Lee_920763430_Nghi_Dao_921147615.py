import socket
import json

ip_blocklist = ["", "", ""] #include whatever IPs to block in this list
# ip_blocklist = ["127.0.0.1"] # for testing


proxy_server_host, proxy_server_port  = "127.0.0.1", 50000
    
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
    proxy_socket.bind((proxy_server_host, proxy_server_port)) #basically bind port number 50000 to the proxy-server
    proxy_socket.listen()
    print("proxy server socket listening")
    while True:
        client_connection, address = proxy_socket.accept() #if there is connection accept the connection request
        # the connection req will be from client
        with client_connection:
            print("proxy server connected")
            data = client_connection.recv(1024).decode() #gets the data

            parsed_json_data = json.loads(data)
            # get the actual data here
            # get the values of JSON by querying using the keys
            data_server_ip = parsed_json_data["server_ip"]
            data_server_port = parsed_json_data["server_port"]
            data_message = parsed_json_data["message"]

            #print(data_message)

            if data_server_ip in ip_blocklist: # check if it's in the IP blocklist
                error_message = "Error"
                client_connection.sendall(error_message.encode()) # send the error right back to client
            else:
                # a new socket to connect to the server
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as new_socket:
                    # connect to server
                    new_socket.connect((data_server_ip, data_server_port))
                    new_socket.sendall(data_message.encode())

                    # getting back response from the server
                    response = new_socket.recv(1024).decode()

                    # send it back to the client
                    client_connection.sendall(response.encode())
                    # return response