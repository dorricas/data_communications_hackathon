import time
import socket
import struct
import threading
from queue import Queue

EXPECTED_MAGIC_CO0KIE = 0xabcddcba


port_pool = Queue()
for port in range(50000, 50100):  # Example port range for UDP connections
    port_pool.put(port)


def get_port():
    """Get a port from the port pool."""
    return port_pool.get()


def release_port(port):
    """Release a port back to the port pool."""
    port_pool.put(port)



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


    file_size = int(input("please input file size: "))
    tcp_conn_num = int(input("please input TCP connection number: "))
    udp_conn_num = int(input("please input UDP connection number: "))

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.bind(("", 12345))  # Bind to the broadcast port

    print("Client started, listening for offer requests...")

    expected_message_type = 0x2

    while True:
        data, server_address = udp_socket.recvfrom(1024)
        try:
            magic_cookie, message_type, server_udp_port, server_tcp_port = struct.unpack('!I B H H', data)
            if magic_cookie == EXPECTED_MAGIC_CO0KIE and message_type == expected_message_type:
                print(f"Received offer from {server_address[0]}")

                tcp_thread = threading.Thread(target=tcp_connection, args=(server_tcp_port, server_address[0]))
                tcp_thread.start()
                # while True:
                #     to_connect = input("Do you want to connect to server? (y/n): ")
                #     if to_connect == "y":
                #         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #         server_ip, _ = server_address
                #         client_socket.bind(('', tcp_port))
                #         print((server_ip, tcp_port))
                #         client_socket.connect((server_ip, tcp_port))
                #
                #         print('Connected to server')
                #         message = f"Hello! I'm client {client_name}"
                #         client_socket.sendall(message.encode())
                #
                #         data = client_socket.recv(1024)
                #         print(data.decode())
                #
                #         print('Closing connection')
                #         client_socket.close()
                #
                #
                #
                #     if to_connect == "n":
                #         break



        except struct.error:
            print("Received malformed offer message.")

def tcp_connection(server_port, server_ip):
    """Handle a single TCP connection."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            print((server_ip, server_port))
            tcp_socket.connect((server_ip, server_port))
            print(f"TCP connection established with {server_ip}:{server_port}")

            while True:
                message = "Hello, TCP server!"
                tcp_socket.sendall(message.encode())
                response = tcp_socket.recv(1024)
                print(f"Received from TCP server: {response.decode()}")
                time.sleep(2)  # Simulate periodic communication
    except Exception as e:
        print(f"TCP connection error: {e}")


def udp_connection(server_port, server_ip):
    source_port = get_port()  # Get a port from the pool
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.bind(("", source_port))
            print(f"UDP connection bound to port {source_port}")

            while True:
                message = "Hello, UDP server!"
                udp_socket.sendto(message.encode(), (server_ip, server_port))
                response, addr = udp_socket.recvfrom(1024)
                print(f"Received from UDP server: {response.decode()}")
                time.sleep(2)  # Simulate periodic communication
    except Exception as e:
        print(f"UDP connection error: {e}")
    finally:
        release_port(source_port)  # Release the port back to the pool


if __name__ == "__main__":
    start_client()
