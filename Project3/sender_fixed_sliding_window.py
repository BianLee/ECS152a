import time
import socket

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE
WINDOW_SIZE = 100

packet_send_times = dict()
packet_delays_list, jitter_values_list = list(), list()

with open('file.mp3', 'rb') as f:
    data = f.read()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
    udp_socket.bind(("127.0.0.1", 5000))
    udp_socket.settimeout(1)

    start = time.time()  # starting timer once socket is created
    total_bytes_sent = 0
    
    seq_id = 0  # initialize at 0
    while seq_id < len(data):
        messages = list()
        acks = dict()
        seq_id_tmp = seq_id
        
        for i in range(WINDOW_SIZE):
            if seq_id_tmp >= len(data):
                break

            message = int.to_bytes(seq_id_tmp, SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id_tmp:seq_id_tmp + MESSAGE_SIZE]
            messages.append((seq_id_tmp, message))
            acks[seq_id_tmp] = False
            total_bytes_sent += len(message)
            seq_id_tmp += MESSAGE_SIZE

        for sid, message in messages:
            udp_socket.sendto(message, ('127.0.0.1', 5001))
            
            packet_send_times[sid] = time.time() #store send time of each packet by using sid as the key in the dictionary (hashmap)
            
        # waiting for ack
        while True:
            try:
                ack, _ = udp_socket.recvfrom(PACKET_SIZE)
                ack_time = time.time()
                ack_id = int.from_bytes(ack[:SEQ_ID_SIZE], byteorder='big', signed=True)
                #print("received ack_id: ", ack_id)
                
                # Calculate delay for this packet
                if ack_id in packet_send_times:
                    delay = ack_time - packet_send_times[ack_id] #querying the send time by using the ack_id as key and calculating the delay
                    packet_delays_list.append(delay) 
                    # append it to the list of delays so that mean can be computed later
                
                # cumulative ack
                for each_key in list(acks.keys()):
                    if each_key < ack_id:
                        acks[each_key] = True    
                
                if all(acks.values()):
                    break
            except socket.timeout:
                #retransmission 
                for sid, message in messages:
                    if not acks[sid]:
                        # send_time = time.time()
                        udp_socket.sendto(message, ('127.0.0.1', 5001))
                        # keep original send time
                        # packet_send_times[sid] = send_time #overwrite it in this case of retransmission
        
        seq_id += WINDOW_SIZE *MESSAGE_SIZE
    
    finish = time.time()
    time_it_took = finish - start

    # calculatig metrics
    print(total_bytes_sent)
    throughput = total_bytes_sent / time_it_took  


    running_sum=0
    #iterate over each value of delay and compute average
    for i in range(len(packet_delays_list)):
        running_sum += packet_delays_list[i]
    avg_delay = running_sum / len(packet_delays_list)

    for i in range(len(packet_delays_list)):
        if i == 0:
            continue
        else:
            jitter = abs(packet_delays_list[i] - packet_delays_list[i-1])
            jitter_values_list.append(jitter)


    running_jitter_sum = 0
    for i in range(len(jitter_values_list)):
        running_jitter_sum += jitter_values_list[i]
    avg_jitter = running_jitter_sum / len(jitter_values_list)
    
    metric = 0.2*(throughput/2000) + (0.1/avg_jitter) +(0.8/avg_delay)
    
    # print(f"{throughput:.7f},{avg_delay:.7f},{avg_jitter:.7f},{metric:.7f}")

    print(f"throughput: {throughput:.7f}")
    print(f"average delay: {avg_delay:.7f}")
    print(f"average jitter: {avg_jitter:.7f}")
    print(f"metric: {metric:.7f}")



    #kill receiver.py in the docker process once everything is done by sending the ==FINACK== message
        
    # udp_socket.sendto(int.to_bytes(-1, 4, signed=True, byteorder='big'), ('127.0.0.1', 5001))
    packid = -1
    fin_packet = packid.to_bytes(4, signed=True, byteorder='big') + "==FINACK==".encode()
    udp_socket.sendto(fin_packet, ('127.0.0.1', 5001))

    ''' 
    udp_socket.sendto("==FINACK==".encode(), ('127.0.0.1', 5001))
    udp_socket.close()
    ''' 
