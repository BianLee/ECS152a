import socket

HOST = "127.0.0.1"
PORT = 8000
DEST_PORT = 5001
ACK_ID_LEN = 4
MESSAGE_SIZE = 1020

FILE_NAME = "file.mp3"


udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((HOST, PORT))
udp_socket.settimeout(0.5)

with open(FILE_NAME, "rb") as file:
    

    messages = []
    seq_id = []
    cur_id = 0

    while True:
        mes = file.read(MESSAGE_SIZE)
        if not mes:
            break
        messages.append(mes)
        seq_id.append(cur_id)
        cur_id += MESSAGE_SIZE

    messages.append("".encode())
    seq_id.append(cur_id + 1)
    
    
    
    i = 0
    last_ack = 0

    while True:
        
        while (i < len(seq_id) and last_ack >= seq_id[i]+len(messages[i])):
   
            i += 1
        
        if i >= len(seq_id):
            break

        print("Transmitting: ", seq_id[i])

        try:
            
            mes = messages[i]
            packid = seq_id[i].to_bytes(ACK_ID_LEN, signed=True, byteorder='big')
            packet = packid + mes
            udp_socket.sendto(packet, (HOST, DEST_PORT))      
          
            data, _ = udp_socket.recvfrom(MESSAGE_SIZE)
            ack_id = int.from_bytes(data[:ACK_ID_LEN], signed=True, byteorder='big')           
            last_ack = ack_id

        except Exception as e:
            print("Error", seq_id[i], e)


    udp_socket.sendto("==FINACK==".encode(), (HOST, DEST_PORT))

udp_socket.close()

