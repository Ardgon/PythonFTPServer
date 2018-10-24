from transfer.SocketMessages import *


def send_file(socket, filename):
    """ Reads and sends file data across a socket """

    try:
        with open(filename, "rb") as file:
            data_send = file.read(4092)  # protocol limits data of messages to 4091 bits
            print("Sending file... {}...\n".format(filename))
            send_message(socket, data_send)
            if get_message(socket) == "FileExistsError".encode():
                # recipient returns with a message that file being sent already exists on their side
                raise FileExistsError

            while data_send:
                data_send = file.read(4092)
                send_message(socket, data_send)
            send_message(socket, '$END_of_FILE$'.encode())  # send an E.O.F. message to verify file has finished sending
        return True

    except FileNotFoundError:
        print("Failure: {} could not be found".format(filename))
        send_message(socket, "{} does not exist".format(filename).encode())  # inform recipient not to expect file
        return False

    except FileExistsError:
        print("Failure: {} already exists".format(filename))
        return False

    except OSError as e:
        print("Failure opening file: {}".format(e))


def receive_file(socket, filename):
    """ Receive data over the socket and write it to a file """

    try:
        data_recv = get_message(socket)
        try:
            if data_recv.decode() == "{} does not exist".format(filename):  # if sent a FileNotFoundError stop receiving
                raise FileNotFoundError
        except UnicodeDecodeError:
            pass  # if data can't be decoded through utf-8 assume it is part of an encoded file, eg zip file

        with open(filename, "xb") as file:
            send_message(socket, "OK".encode())  # confirm it is ok to start sending file
            print("Receiving file... {}...\n".format(filename))
            while data_recv:
                file.write(data_recv)
                data_recv = get_message(socket)
            data_recv = get_message(socket)
            if data_recv == '$END_of_FILE$'.encode():  # return True once E.O.F. is received
                    return True

            print('Failure: unexpected error receiving messages')
            raise MessageError  # ideally should never be raised

    except FileExistsError:
        print("Failure: {} already exists".format(filename))
        send_message(socket, "FileExistsError".encode())  # inform sender the file already exists on recipient's side
        return False

    except FileNotFoundError:
        print("Failure: {} could not be found".format(filename))
        return False

    except OSError as e:
        print("Failure creating file: {}".format(e))
