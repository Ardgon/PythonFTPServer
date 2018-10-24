from transfer.Files import send_file, receive_file
from transfer.SocketMessages import *
import socket
import sys


class Client:
    def __init__(self, address, port, request):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        except socket.error as e:
            print("Error creating socket: {}".format(e))
            sys.exit(1)

        self.request = request
        self.connect(address, port)

    def connect(self, connect_address, connect_port):
        """ Connects to target host """
        try:
            self.sock.connect((connect_address, connect_port))
            print("Connected to host: {} port: {}\n".format(connect_address, connect_port))

        except socket.gaierror as e:
            print("Address-related error connecting to server: {}".format(e))
            sys.exit(1)

        except socket.error as e:
            print("Connection error: {}".format(e))
            sys.exit(1)

        except OverflowError:
            print("Port must be 0-65535")
            sys.exit(1)

        try:
            self.process_input()
        except MessageError:  # should never raise
            sys.exit(1)

    def disconnect(self):
        """ Closes connection with host """

        self.sock.close()
        print("Disconnected from host")

    def client_list(self):
        """ Receives list of files in server's directory """

        print("Requesting current directory of host... \n")
        send_message(self.sock, 'list'.encode())
        recv_message = get_message(self.sock)
        while recv_message:
            print(" - {}".format(recv_message.decode()))
            recv_message = get_message(self.sock)
        print()

    def client_put(self, filename):
        """ Sends file to server """

        print("Requesting permission from host to send {}...\n".format(filename))
        send_message(self.sock, 'put'.encode())
        send_message(self.sock, filename.encode())
        if send_file(self.sock, filename):
            print("File successfully sent to host\n")
        else:
            sys.exit(1)

    def client_get(self, filename):
        """ Receives file from server """

        print("Requesting {} from host...".format(filename))
        print()
        send_message(self.sock, 'get'.encode())
        send_message(self.sock, filename.encode())
        if receive_file(self.sock, filename):
            print("File received from host\n")
        else:
            sys.exit(1)

    def process_input(self):
        """ Processes (list, put, get) requests sent to server """

        try:
            while True:
                if not self.request:
                    print("No request specified!\n")
                    break
                elif len(self.request) > 2:
                    raise IndexError
                elif self.request[0] == 'list':
                    self.client_list()
                    break
                elif self.request[0] == 'put':
                    self.client_put(self.request[1])
                    break
                elif self.request[0] == 'get':
                    self.client_get(self.request[1])
                    break
                else:
                    print("Unknown request: {}\n".format(self.request[0]))
                    send_message(self.sock, self.request[0].encode())
                    break

        except IndexError:
            print("Invalid request: {}\n".format(' '.join(self.request)))

        self.disconnect()  # close connection after request has been processes


if __name__ == "__main__":

    server_ip = sys.argv[1]  # ip of target host (ip, port and request should be given as commandline arguments)
    try:
        server_port = int(sys.argv[2])
    except ValueError:
        print("Incorrect port, port number must be an integer 0-65535")
        sys.exit(1)

    if len(sys.argv) > 3:  # check if all arguments have been provided
        requests = sys.argv[3:]
        Client(server_ip, server_port, requests)
    else:
        print("Incorrect amount of arguments, use: Server.py <address> <port> <request>\n")
