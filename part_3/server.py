import socket

server_host, server_port = "127.0.0.1",50005

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((server_host, server_port)) # bind port number 50005 to the server
    server_socket.listen()
    print("server socket listening")

    while True:
        # waiting for connection. when te proxy server connects accept that.
        proxy_server_connection, address = server_socket.accept() #if there is connection accept the connection request
        with proxy_server_connection:
            print("server socket connected")
            data = proxy_server_connection.recv(1024).decode() # data from the proxy server
            proxy_server_connection.sendall(data.encode()) #send it right back to proxy server (this is a ping pong after all)