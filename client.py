import socket
import struct

EXPECTED_MAGIC_CO0KIE = 0xabcddcba


def start_client():
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_address = ('localhost', 65431)
    #
    # print(f"Connecting to server at {server_address[0]}:{server_address[1]}")
    # client_socket.connect(server_address)
    #
    # try:
    #     messages = ["Hello, Server!", "How are you?", "Goodbye!"]
    #     for message in messages:
    #         print(f"Sending: {message}")
    #         client_socket.sendall(message.encode())
    #
    #         data = client_socket.recv(1024)
    #         print(f"Received: {data.decode()}")
    # finally:
    #     print("Closing connection")
    #     client_socket.close()

    client_name = input("Enter client name: ")

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.bind(("", 12345))  # Bind to the broadcast port



    print("Listening for server offers...")

    expected_message_type = 0x2

    while True:
        data, server_address = udp_socket.recvfrom(1024)
        try:
            magic_cookie, message_type, udp_port, tcp_port = struct.unpack('!I B H H', data)
            if magic_cookie == EXPECTED_MAGIC_CO0KIE and message_type == expected_message_type:
                print(f"Received offer from {server_address}: UDP port {udp_port}, TCP port {tcp_port}")
                while True:
                    to_connect = input("Do you want to connect to server? (y/n): ")
                    if to_connect == "y":
                        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        server_ip, _ = server_address
                        client_socket.bind(('', tcp_port))
                        print((server_ip, tcp_port))
                        client_socket.connect((server_ip, tcp_port))

                        print('Connected to server')
                        message = f"Hello! I'm client {client_name}"
                        client_socket.sendall(message.encode())

                        data = client_socket.recv(1024)
                        print(data.decode())

                        print('Closing connection')
                        client_socket.close()



                    if to_connect == "n":
                        break



        except struct.error:
            print("Received malformed offer message.")


if __name__ == "__main__":
    start_client()
