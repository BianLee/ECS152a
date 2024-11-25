import socket
import random
import time

DNS_PORT = 53
HTTP_PORT = 80
website = "tmz.com"

DNS_SERVERS = [
    '198.41.0.4',
    '170.247.170.2',
    '192.33.4.12',
    '199.7.91.13',
    '192.203.230.10',
    '192.5.5.241',
    '192.112.36.4',
    '198.97.190.53',
    '192.36.148.17',
    '192.58.128.30',
    '193.0.14.129',
    '199.7.83.42',
    '202.12.27.33',
]


class Byte_Decoder:
    def __init__(self, byte_data: bytes):
        """
        Initialize the ByteReader with a sequence of bytes.
        """
        self.byte_data = byte_data
        self.index = 0

    def next_byte(self):
        """
        Read the next byte. Return None if the end is reached.
        """
        if self.index < len(self.byte_data):
            byte = self.byte_data[self.index]
            self.index += 1
            return byte
        else:
            return None

    def next_n_bytes(self, n):
        rd_bytes = ''.encode()
        for i in range(n):
            rd_bytes += self.next_byte().to_bytes(1)
        return rd_bytes

    
    def next_int(self, length):
        number = 0
        for i in range(length):
            number = (number << 8) + int(self.next_byte())
        return number

    def next_char(self, length):
        string = ''
        for i in range(length):
            string += chr(self.next_byte())
        return string

    def next_name(self):
        name = ''
        while True:
            id = self.next_int(1)
            if id == 0:
                return name

            if name != '':
                name += '.'
                
            if id >= 64:
                index = self.index
                self.index = (int(id & 0b111111) << 8) + self.next_int(1)
                name += self.next_name()
                self.index = index + 1
                return name
            else:
                length = int(id & 0b111111)
                name += self.next_char(length)
        return name


class DNS_Question_Decoder:
    def __init__(self, decoder):
        self.name = decoder.next_name()
        self.type = int(decoder.next_int(2))
        self.clss = int(decoder.next_int(2))
    def __str__(self):
        return f"Name: {self.name}  |  Type: {self.type}  |  Class: {self.clss}"


class DNS_Record_Decoder:
    def __init__(self, decoder):
        self.name = decoder.next_name()
        self.type = int(decoder.next_int(2))
        self.clss = int(decoder.next_int(2))
        self.ttl = int(decoder.next_int(4))
        self.rd_len = int(decoder.next_int(2))


        self.rd = 0
        if self.type == 28:
            self.rd = self.ip6(decoder.next_n_bytes(self.rd_len))
        elif self.type == 1:
            self.rd = self.ip4(decoder.next_n_bytes(self.rd_len))
        elif self.type == 2:
            self.rd = decoder.next_name()
        else:
            self.rd = decoder.next_n_bytes(self.rd_len)

    def __str__(self):
        return f"Name: {self.name}  |  Type: {self.type}  |  Class: {self.clss}  |  TTL: {self.ttl}  |  RD len: {self.rd_len}  |  RD: {str(self.rd)}"

    def ip4(self, byte_data):
        if len(byte_data) != 4:
            raise ValueError("Input must be exactly 4 bytes")
        return '.'.join(str(byte) for byte in byte_data)

    def ip6(self, byte_data):
        if len(byte_data) != 16:
            raise ValueError("Input must be exactly 16 bytes")
        groups = [f"{byte_data[i]:02x}{byte_data[i + 1]:02x}" for i in range(0, 16, 2)]
        return ":".join(groups)
        


class DNS_Decoder:
    def __init__(self, bytes):
        decoder = Byte_Decoder(bytes)
        self.id = decoder.next_int(2)
        self.flags = decoder.next_int(2)
        self.qd_count = decoder.next_int(2)
        self.ans_count = decoder.next_int(2)
        self.ns_count = decoder.next_int(2)
        self.ar_count = decoder.next_int(2)
    
        self.questions = []
        self.answers = []
        self.authorities = []
        self.additionals = []
        
        for i in range(self.qd_count):
            self.questions.append(DNS_Question_Decoder(decoder))
        
        for i in range(self.ans_count):
            self.answers.append(DNS_Record_Decoder(decoder))
        
        for i in range(self.ns_count):
            self.authorities.append(DNS_Record_Decoder(decoder))
            
        for i in range(self.ar_count):
            self.additionals.append(DNS_Record_Decoder(decoder))



class DNS_Encoder:
    def __init__(self, websites, type=1):
        id = self.int_to_bytes(random.randint(0, 2**(16)-1), 2)
        flags = self.int_to_bytes(0, 2) # no recursion
        qd_count = self.int_to_bytes(len(websites), 2)
        ans_count = self.int_to_bytes(0, 2)
        ns_count = self.int_to_bytes(0, 2)
        ar_count = self.int_to_bytes(0, 2)
    
        header = id + flags + qd_count + ans_count + ns_count + ar_count
        payload = ''.encode()
        
        for web in websites:
            payload += self.website_to_bytes(web, type)
        
        self.message = header + payload
        
    def int_to_bytes(self, number, count):
        return number.to_bytes(count, 'big')
    
    def website_to_bytes(self, website, type=1):
        total_len = 0
        names = website.split(".")
        
        bytes = ''.encode()
        
        for str in names:
            bytes += self.int_to_bytes(len(str), 1)
            bytes += str.encode()
    
        bytes += self.int_to_bytes(0, 1) # null char
        bytes += self.int_to_bytes(type, 2) # qtype
        bytes += self.int_to_bytes(1, 2) # qclass
            
        return bytes

    

def resolve_ip(search_ath):
    for rec in search_ath.authorities:
        aut_name = rec.rd
        aut_ip = 0
        for record in search_ath.additionals:
            if record.name == aut_name and record.type == 1:
                aut_ip = record.rd
                break

        if aut_ip != 0:
            return aut_ip

    return search(search_ath.authorities[0].rd)

def search_dns_server(websites, dns_ip):

    root_response = None
    tld_response = None
    aut_response = None
    
    ns_request = DNS_Encoder(websites, 2).message
    a_request = DNS_Encoder(websites, 1).message
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:

        client.sendto(ns_request, (dns_ip, DNS_PORT))
        response, _ = client.recvfrom(1024)
        root_response = DNS_Decoder(response)


        tld_ip = resolve_ip(root_response)

        client.sendto(ns_request, (tld_ip, DNS_PORT))
        response, _ = client.recvfrom(1024)
        tld_response = DNS_Decoder(response)



        aut_ip = resolve_ip(tld_response)

        client.sendto(a_request, (aut_ip, DNS_PORT))
        response, _ = client.recvfrom(1024)
        aut_response = DNS_Decoder(response)

        return aut_response.answers[0].rd


def search(website):
    for dns_ip in DNS_SERVERS:
        try:
            ip = search_dns_server([website], dns_ip)
            return ip
        except Exception as e:
            time.sleep(10)
            


start_time = time.time()
ip_address = search(website)
end_time = time.time()

print("ip: ", ip_address)
print("RTT of dns resolver:", end_time - start_time)
 


start_time = time.time()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((ip_address, HTTP_PORT))
    request = "GET / HTTP/1.1\r\nHost: " + website + "\r\nConnection: close\r\n\r\n"
    client_socket.sendall(request.encode())
    response = client_socket.recv(1024)

end_time = time.time() 
print("RTT of http request:", end_time - start_time)     


