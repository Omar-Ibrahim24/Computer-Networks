import struct
import socket
import datetime
import os


class UDPTOTCP:

    def __init__(self, server_address):
        # create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # set server address
        self.server_address = server_address

        # set sequence number
        self.seq_num = 0

        self.sock.bind(self.server_address)

        # Message Sent
        self.data = ''

        self.SYN = "0"
        self.SYN_ACK = "0"
        self.ACK = "0"
        self.FIN = "0"



    def send_packet(self, message):
        # calculate checksum
        checksum = self._calculate_checksum(message)
        # pack data and checksum into a struct
        packet = struct.pack('!I', checksum) + message
        # send packet to server
        self.sock.sendto(packet, self.server_address)

        # wait for ACK
        while True:
            data, server = self.sock.recvfrom(4096)
            # unpack ACK data
            ack_num, = struct.unpack('!I', data)

            # check if ACK matches sequence number
            if ack_num == self.seq_num:
                self.seq_num = 1 - self.seq_num






    def handshake(self):
        # Receive SYN_Flag
        syn, server = self.sock.recvfrom(4096)
        syn = syn.decode()

        print("server recieved syn is ", syn)
        if syn[0] == "1":
            self.SYN = "1"
            self.SYN_ACK = "1"
            handshake_flags = (self.SYN + self.SYN_ACK + self.ACK)
            print("server sent flags", handshake_flags)
            self.sock.sendto(handshake_flags.encode('utf-8'), server)

        # Receive ACK_Flag
        ack, server = self.sock.recvfrom(4096)
        ack = ack.decode()
        if syn[2] == "1":
            self.ACK = "1"
            print("SYN is", self.SYN)
            print("SYN_ACK is", self.SYN_ACK)
            print("ACK", self.ACK)
            # Connection established
            print("Connection established with client at address:", server)

    def receive_packet(self):
        while 1:


            # receive packet from server
            data, server = self.sock.recvfrom(4096)

            # unpack packet data
            if len(data) >= 8:
                seq_num, checksum = struct.unpack('!II', data[:8])
                print("sequence", seq_num)
                print("checksum", checksum)

                # Packet_data is the packet sent without sequence numbe and checksum
                packet_data = data[8:]

                if packet_data.decode() == "FIN":

                    self.sock.close()
                    break

                self.data = packet_data.decode()

                # check packet checksum
                if self._verify_checksum(packet_data, checksum):
                    # send ACK to server
                    arr = [seq_num]
                    for i in range(1):
                        ack_packet = struct.pack('!I', arr[i])
                        self.sock.sendto(ack_packet, server)
            else:
                print("empty message")

            # Create Object of HTTP Request
            httpREC = HTTPRequest()

            # Parse_request is used to split message into Method,headers,body
            httpREC.parse_request(self.data)

            # Check Existence of File to write status code
            if os.path.exists(httpREC.uri):
                status_code = " 200 OK"
            else:
                status_code = " 404 Not Found"

            # GET Method
            if httpREC.method == 'GET':
                if status_code == " 200 OK":

                    with open(httpREC.uri, "r") as f:
                        lines = ''
                        for line in f:
                            lines += line

                        # Content Length Header
                        conlen = "Content-Length:" + str(len(lines)) + "\r\n"
                else:
                    lines = ''
                    conlen = "Content-Length:" + str(len(lines)) + "\r\n"
            # POST Methods
            elif httpREC.method == 'POST':
                if status_code == " 200 OK":
                    with open(httpREC.uri, "a") as f:
                        f.write("\n")
                        f.write(httpREC.body)

            # ******************Headers*****************
            # Status Line
            first = httpREC.version + status_code + "\r\n"
            # Datetime Header
            current_date = datetime.date.today()
            date = "Date :" + str(current_date) + "\r\n"

            if httpREC.method == 'GET':
                data_response = first + date + conlen + lines
            else:
                data_response = first + date

            # Send response to Client
            print("HTTP Response to Client is", data_response)

            self.sock.sendto(data_response.encode('utf-8'), server)

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


class HTTPRequest:
    def __init__(self, headers=None):
        # Constructor of HTTP Request Message that contains Method,URL,Version,Headers,and body of request
        self.method = None
        self.uri = None
        self.version = None
        self.headers = headers if headers is not None else {}
        self.body = ''

    def parse_request(self, request_string):
        # Parse Request is used to split the request into Method,URL,Version,Headers,and body of request
        lines = request_string.split('\r\n')
        request_line = lines[0].split()
        self.method = request_line[0]
        self.uri = request_line[1]
        self.version = request_line[2]

        if self.method == 'POST':
            self.body = lines[-1]
        for i in range(1, len(lines) - 2):
            header_name, header_value = lines[i].split(': ')
            self.headers[header_name] = header_value


if __name__ == "__main__":
    # Assign Ip Address and Port Number Used
    ServerAddress = ('localhost', 9999)
    # Create Object Of UDPTOTCP Class
    server = UDPTOTCP(ServerAddress)
    # server.handshake()
    server.receive_packet()
