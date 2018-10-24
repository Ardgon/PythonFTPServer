import socket
import struct


class MessageError(Exception):
    """ Raised when Sending/Receiving messages fails """
    pass


def send_message(sock, message):
    """ Send a message to a socket, prepended by its length packed in 4 bytes (big endian)."""

    data = message
    length = struct.pack('>L', len(message))
    try:
        sock.sendall(length + data)

    except socket.error as e:
        print("Error sending data: {}".format(e))
        raise MessageError


def get_message(sock):
    """ Read a message from a socket. """

    length = socket_read_n(sock, 4)
    length = struct.unpack('>L', length)[0]

    message = socket_read_n(sock, length)

    return message


def socket_read_n(sock, n):
    """ Read exactly n bytes from the socket. Raise MessageError if the connection is closed before n bytes were read"""

    buf = bytes()
    try:
        while n > 0:
            data = sock.recv(n)
            if data == '':
                return "0"
            buf += data
            n -= len(data)  # Stop reading after receiving n bytes

    except socket.error as e:
        print("Error receiving data: {}".format(e))
        raise MessageError()

    return buf
