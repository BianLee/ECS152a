import socket
import time

HOST = "127.0.0.1"
PORT = 8000
DEST_PORT = 5001
ACK_ID_LEN = 4
MESSAGE_SIZE = 1020

FILE_NAME = "file.mp3"


udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((HOST, PORT))
udp_socket.settimeout(0.3)

with open(FILE_NAME, "rb") as file:
    

    messages = []
    expected = []
    seq_id = []
    cur_id = 0

    while True:
        mes = file.read(MESSAGE_SIZE)
        if not mes:
            break
        messages.append(mes)
        seq_id.append(cur_id)
        cur_id += len(mes)
        expected.append(cur_id)
        

    messages.append("".encode())
    seq_id.append(cur_id)
    expected.append(cur_id + 1)
    
    
    i = 0
    last_ack = 0
    total_jitter = 0

    packet_timer = time.time()
    last_delay = 0
    timer = time.time()
    total_delay = 0
    packet_count = 0

    while True:
        
        while i < len(seq_id) and last_ack >= expected[i]:
            i += 1
            packet_timer = time.time()
             
        if i >= len(seq_id):
            break
     
        try:
            
            mes = messages[i]
            packid = seq_id[i].to_bytes(ACK_ID_LEN, signed=True, byteorder='big')
            packet = packid + mes
            udp_socket.sendto(packet, (HOST, DEST_PORT))      
            
            # print("Transmitting:", seq_id[i])

            data, _ = udp_socket.recvfrom(MESSAGE_SIZE)
            ack_id = int.from_bytes(data[:ACK_ID_LEN], signed=True, byteorder='big')           
            last_ack = ack_id
             
            if last_ack > seq_id[i]:
                delay = time.time() - packet_timer
                time_diff = abs(last_delay - delay)
                total_jitter += time_diff
                last_delay = delay
                total_delay += delay
                packet_count += 1

        except Exception as e:
            # print("Error", seq_id[i], e)


    packid = -1
    # print("Final ack:", last_ack)
    # print("Send ==FINACK==")
    fin_packet = packid.to_bytes(ACK_ID_LEN, signed=True, byteorder='big') + "==FINACK==".encode()
    udp_socket.sendto(fin_packet, (HOST, DEST_PORT))
    
    avg_jitter = total_jitter/packet_count
    avg_delay = total_delay/packet_count
    throughput = seq_id[len(seq_id)-1]/(time.time() - timer)

    print("Stop and wait")
    print("Throughput (KB/s):", throughput)
    print("Average Jitter (s):", avg_jitter)
    print("Average Delay (s):", avg_delay)
    print("Metric:", 0.2 * throughput/2000 + 0.1/avg_jitter + 0.8/avg_delay)

udp_socket.close()
