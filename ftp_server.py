import socket
import threading
import os # for listing files
from _thread import *
import sys

control_port = 4139
data_port = 4141
thread_count = 0
host = ''


def lst(client, server):
    print("Recieved LIST command")
    client.send(data_port.to_bytes(4, byteorder='big', signed=False))
    print("Listening for data connection...")
    data_connection, daata_addr = server.accept()
    print("Connection accepted. Sending files...")
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    return_data = ''
    for f in files:
        return_data += f + '\n'
    size_of_data = len(return_data.encode('utf-8'))
    data_connection.send(size_of_data.to_bytes(1024, byteorder='big', signed=False))
    data_connection.send(return_data.encode(encoding='ascii'))
    print("Data sent. Closing data connection...")
    data_connection.close()


def retr(client, server, file_name: str):
    print("File exists! Opening data connection...")
    client.send(data_port.to_bytes(4, byteorder='big', signed=True))
    print("Listening for data connection...")
    data_connection, data_addr = server.accept()
    print("Connection accepted. Sending file size...")
    f = open(file_name, 'rb')
    file_size = os.path.getsize(file_name)
    data_connection.send(file_size.to_bytes(1024, byteorder='big', signed=False))
    print("File size sent. Sending file...")
    file_data = f.read()
    # file_data = file_data.encode('ascii')
    f.close()
    data_connection.send(file_data)
    print("File sent. Closing connection...")
    data_connection.close()


def stor(client, server, file_name):
    print("Recieved STOR command")
    client.send(data_port.to_bytes(4, byteorder='big', signed=False))
    print("Listening for data connection...")
    data_connection, data_addr = server.accept()
    print("Connection accepted. Recieving file size...")
    file_size = False
    while not file_size:
        file_size = data_connection.recv(4)
    file_data = False
    while not file_data:
        file_data = data_connection.recv(int.from_bytes(file_size, byteorder='big', signed=False))
    f = open(file_name, 'wb')
    f.write(file_data)
    f.close()
    print("Data recieved. Closing connection...")
    data_connection.close()


def threaded(client, server):
    while True:
        control_data = client.recv(1024)
        control_data = control_data.decode('ascii')
        control_data = control_data.split(' ')
        if control_data[0] == 'LIST':
            lst(client, server)
        elif control_data[0] == 'RETR':
            print("Recieved RETR command. Checking if file exists...")
            if os.path.isfile(control_data[1]):
                retr(client, server, control_data[1])
            else:
                response = -1
                print("File does not exist! Sending response to client...")
                client.send(response.to_bytes(4, byteorder='big', signed=True))
        elif control_data[0] == 'STOR':
            stor(client, server, control_data[1])
        elif control_data[0] == 'QUIT':
            print("QUIT command recieved. Ending connection...")
            client.close()
            break
        else:
            client.close()
            break


#############################
# Main function begins here #
#############################
def main():
    thread_count = 0
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sckt.bind((host, control_port))
    data_sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_sckt.bind((host, 4141))
    data_sckt.listen()
    sckt.listen(20)
    while True:
        client, addr = sckt.accept()
        thread_count += 1
        print('Connection to ', addr, ':', control_port)
        start_new_thread(threaded, (client, data_sckt))


if __name__ == '__main__':
    main()

# Sources:
# https://www.geeksforgeeks.org/socket-programming-multi-threading-python/
