from threading import Thread
from transfer.Files import send_file, receive_file
from transfer.SocketMessages import *

import socket
import sys
import os


class ListenToClient(Thread):
    def __init__(self, sock, address):
        Thread.__init__(self)
        self.sock = sock
        self.addr = address
        self.start()

    def server_list(self):
        """ Send all file names in the server's directory """

        print("Client: {} port: {} Issued a list request".format(self.addr[0], self.addr[1]))
        current_dir = [file for file in os.listdir(".") if (os.path.isfile(file) and file != "Server.py")]  # only files
        for filename in current_dir:
            send_message(self.sock, filename.encode())

        print("Client: {} port: {} Request processed successfully".format(self.addr[0], self.addr[1]))

    def server_get(self):
        """ Send file to client """

        filename = get_message(self.sock).decode()
        print("Client: {} port: {} Requested get {}".format(self.addr[0], self.addr[1], filename))
        if send_file(self.sock, filename):
            print("Client: {} port: {} Request processed successfully".format(self.addr[0], self.addr[1]))
        else:
            print("Client: {} port: {} Get request Failed".format(self.addr[0], self.addr[1]))
            self.disconnect()

    def server_put(self):
        """ Receive file from client """

        filename = get_message(self.sock).decode()
        print("Client: {} port: {} Requested put {}".format(self.addr[0], self.addr[1], filename))
        if receive_file(self.sock, filename):
            print("Client: {} port: {} Request processed successfully".format(self.addr[0], self.addr[1]))
        else:
            print("Client: {} port: {} Put request Failed".format(self.addr[0], self.addr[1]))
            self.disconnect()

    def disconnect(self):
        """ Close client connection """

        self.sock.close()
        print("Client: {} port: {} Disconnected\n".format(self.addr[0], self.addr[1]))
        sys.exit(1)

    def process_request(self):
        """ Processes (list, get, put) requests from client """

        try:
            while True:
                recv_message = get_message(self.sock).decode()

                if recv_message == 'list':
                    self.server_list()
                    self.disconnect()

                elif recv_message == 'get':
                    self.server_get()
                    self.disconnect()

                elif recv_message == 'put':
                    self.server_put()
                    self.disconnect()

                else:
                    print(
                        "Client: {} port: {} INVALID REQUEST: {}".format(self.addr[0], self.addr[1], recv_message))
                    self.disconnect()

        except ConnectionResetError:
            self.sock.close()
            print("Client: {} port: {} Has disconnected".format(self.addr[0], self.addr[1]))
            return

    def run(self):
        print('Client: {} port: {} Connection established'.format(self.addr[0], self.addr[1]))

        try:
            self.process_request()
        except MessageError:  # Should never raise
            self.disconnect()


if __name__ == "__main__":

    def server_start():
        """ Initialises server socket """
        srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            bind_ip = "0.0.0.0"
            bind_port = int(sys.argv[1])  # port should be given as commandline argument

            srv_sock.bind((bind_ip, bind_port))
            print("Binding successful")

        except ValueError:
            print("incorrect port")
            sys.exit(1)

        except OverflowError:
            print("Port must be 0-65535")
            sys.exit(1)

        server_listen(srv_sock)


    def server_listen(sock):
        sock.listen(3)
        while True:  # accept connections
            cli_sock, cli_addr = sock.accept()
            ListenToClient(cli_sock, cli_addr)


    server_start()
