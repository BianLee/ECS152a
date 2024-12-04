import socket
import time

HOST = "127.0.0.1"
PORT = 8000
DEST_PORT = 5001
ACK_ID_LEN = 4
MESSAGE_SIZE = 1020

FILE_NAME = "file.mp3"
TIME_OUT = 0.3

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((HOST, PORT))
udp_socket.settimeout(TIME_OUT)


class TCPTahoe():
    def __init__(self, messages, seq_id, expected_ack):
        self.cwnd = 1
        self.ssthresh = 64
        self.total_jitter = 0
        self.total_delay = 0
        self.packet_count = 0

        self.start = time.time()
        
        last_ack = 0
        win_start = 0
        win_end = 0
        last_delay = 0
        transmit_start = {}
    
        ack_dict = {}
        send_dict = {}
        
        for i in range(len(seq_id)):
            send_dict[seq_id[i]] = i

        while True:
            while win_start < len(messages) and last_ack >= expected_ack[win_start]:
                win_start += 1
                packet_timer = time.time()
            
            
            if win_start >= len (messages):
                break

            
            win_end = min(len(messages), win_start + self.cwnd)
            timer_start = time.time()
           
            # print("Start cwnd:", self.cwnd, "ack:", last_ack)

            try:
                for j in range(win_start, min(len(messages), win_end+1), 1):
                    mes = messages[j]
                    s_id = seq_id[j]
                    packid = s_id.to_bytes(ACK_ID_LEN, signed=True, byteorder='big')
                    packet = packid + mes
                    udp_socket.sendto(packet, (HOST, DEST_PORT))
                    
                    if not s_id in transmit_start:
                        transmit_start[s_id] = time.time()
                     
                duplicate = False

                while True:
                    
                    data, _ = udp_socket.recvfrom(MESSAGE_SIZE)
                    ack_id = int.from_bytes(data[:ACK_ID_LEN], signed=True, byteorder='big')
                        
                    if not ack_id in ack_dict:
                        ack_dict[ack_id] = 0
                        if ack_id > last_ack:
                            if not last_ack in transmit_start:
                                transmit_start[last_ack] = time.time()

                            delay = time.time() - transmit_start[last_ack] 
                            time_diff = abs(last_delay - delay)
                            self.total_jitter += time_diff
                            self.total_delay += delay
                            self.packet_count += 1
                            last_delay = delay
                            

                    ack_dict[ack_id] += 1
                    
                    if ((ack_dict[ack_id]-1) % 3 == 0) and (ack_dict[ack_id] != 1):
                        duplicate = True
                        # print("Triple duplicate for", ack_id, "|", ack_dict[ack_id])
                        
                        break

                    last_ack = max(last_ack, ack_id)
                    
                    if last_ack >= expected[win_end-1]:
                        break
                
                
                if duplicate == False:
                    self.on_success()
                else:
                    self.on_duplicate()

            except Exception as e:
                self.on_timeout()
                # print("Timeout, reached:", last_ack, " | expected:", expected[win_end-1])
        
        self.last_ack = last_ack

    def on_timeout(self):
        self.ssthresh = max(1, self.cwnd//2)
        self.cwnd = 1


    def on_duplicate(self):
        self.ssthresh = max(1, self.cwnd//2)
        self.cwnd = 1 

    def on_success(self):
        if self.cwnd < self.ssthresh:
            self.cwnd = min(self.ssthresh, self.cwnd*2)
        else:
            self.cwnd += 1


with open(FILE_NAME, "rb") as file:
    
    # this is just for calculating total bytes so that it can be used for throughput calc
    data = file.read()
    full_count = len(data) // MESSAGE_SIZE
    remaining = len(data) % MESSAGE_SIZE
    total_bytes_sent = (ACK_ID_LEN + MESSAGE_SIZE)* full_count
    total_bytes_sent += ACK_ID_LEN + remaining

    file.seek(0)
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
    
    
    timer = time.time()
    tahoe = TCPTahoe(messages, seq_id, expected)
    

    packid = -1
    # print("Final ack:", tahoe.last_ack)
    # print("Send ==FINACK==")
    fin_packet = packid.to_bytes(ACK_ID_LEN, signed=True, byteorder='big') + "==FINACK==".encode()
    udp_socket.sendto(fin_packet, (HOST, DEST_PORT))

    throughput = total_bytes_sent / (time.time() - timer)
    avg_jitter = tahoe.total_jitter/tahoe.packet_count
    avg_delay = tahoe.total_delay/tahoe.packet_count
    
    print("Tahoe")
    print(total_bytes_sent)
    print("Throughput (B/s): {:.7f}".format(throughput))
    print("Average Jitter (s): {:.7f}".format(avg_jitter))
    print("Average Delay (s): {:.7f}".format(avg_delay))
    print("Metric: {:.7f}".format(0.2 * throughput / 2000 + 0.1 / avg_jitter + 0.8 / avg_delay))


udp_socket.close()
