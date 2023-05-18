import random
import struct
import socket


class HTTPResponse:
    def __init__(self, headers=None):
        # Constructor of HTTP Respinse Message that contains Version,Headers,and body of response
        self.version = None
        self.headers = headers if headers is not None else {}
        self.body = ''
        self.method = ''

    def parse_response(self, response_string):
        # Parse Response is used to split the response into Version,Headers,and body of response
        lines = response_string.split('\r\n')
        request_line = lines[0].split()
        self.version = request_line[0]
        self.status_code = request_line[1]
        self.status_message = request_line[2]

        if self.method == 'POST':
            self.body = lines[-1]

        for i in range(1, len(lines) - 2):
            header_name, header_value = lines[i].split(':')
            self.headers[header_name] = header_value


class TCPtoUDP:
    def __init__(self, server_address):
        # create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # set a timeout of 5 seconds
        self.sock.settimeout(5)

        # set server address
        self.server_address = server_address

        # set sequence number
        self.seq_num = 0

        # Handshake flags
        self.SYN = "0"
        self.SYN_ACK = "0"
        self.ACK = "0"
        self.FIN = "0"
        self.flag = 1

    def handshake(self):
        self.SYN = "1"
        handshake_flags = (self.SYN + self.SYN_ACK + self.ACK)
        self.sock.sendto(handshake_flags.encode('utf-8'), self.server_address)
        print("Syn flag sent is ", handshake_flags)

        # receive SYN_ACK from server
        syn_ack, server = self.sock.recvfrom(4096)
        syn_ack = syn_ack.decode()
        print("syn_ack flag recieved", syn_ack)
        # Send ACK to Server
        if syn_ack[1] == "1":
            self.SYN_ACK = "1"
            self.ACK = "1"
            handshake_flags = (self.SYN + self.SYN_ACK + self.ACK)
            print("ack flag sent is ", handshake_flags)
            self.sock.sendto(handshake_flags.encode('utf-8'), server)

    def send_packet(self, message):
        # calculate checksum
        checksum = self._calculate_checksum(message)

        # pack data and checksum into a struct
        packet = struct.pack('!I', self.seq_num) + struct.pack('!I', checksum) + message

        # send packet to server
        self.sock.sendto(packet, self.server_address)

        # wait for ACK
        while self.flag:

            try:
                # receive ACK from server
                if message.decode() == 'FIN':
                    self.flag=0
                    break
                data, server = self.sock.recvfrom(4096)
                # unpack ACK data
                ack_num, = struct.unpack('!I', data)

                # check if ACK matches sequence number
                if ack_num == self.seq_num:
                    self.seq_num = 1 - self.seq_num
                    httpresponse = HTTPResponse()
                    http_resp, server = client.sock.recvfrom(4096)
                    httpresponse.method = message[0:4]
                    httpresponse.parse_response(http_resp.decode())

                    print("*****HTTP Response********\n")
                    print(http_resp.decode())
                    break

            except socket.timeout:
                self.send_packet(message)

    def _calculate_checksum(self, data):
        # sum bytes in data
        sum = 0
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                sum += (data[i] << 8) + data[i + 1]
            else:
                sum += data[i]

        # fold sum into 16 bits
        sum = (sum >> 16) + (sum & 0xffff)
        sum += (sum >> 16)

        # return 1's complement of sum
        return ~sum & 0xffff

    def _verify_checksum(self, data, checksum):
        # calculate checksum of data
        calculated_checksum = self._calculate_checksum(data)
        # compare calculated checksum with received checksum
        return calculated_checksum == checksum

    def close(self):
        msg = "FIN"
        self.send_packet(msg.encode('utf-8'))
        self.sock.close()


# Main Function
if __name__ == "__main__":
    ServerAddress = ('localhost', 9999)
    client = TCPtoUDP(ServerAddress)
    # client.handshake()
    msg = "POST data.txt HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate, br\r\nConnection: keep-alive\r\nReferer: https://www.google.com/\r\nUpgrade-Insecure-Requests: 1\r\n\r\nNEW DATA"
    client.send_packet(msg.encode('utf-8'))
    client.send_packet(msg.encode('utf-8'))

    client.close()
