import time
import socket
import struct
import threading
from queue import Queue


LOCALHOST = "localhost"
EXPECTED_MAGIC_CO0KIE = 0xabcddcba
FIRST_UDP_PORT = 50000
LAST_UDP_PORT = 60000
OFFER_PORT = 12345
CHUNK_SIZE = 1024
OFFER_MESSAGE_TYPE = 0x2
REQUEST_MESSAGE_TYPE = 0x3


port_pool = Queue()
for port in range(FIRST_UDP_PORT, LAST_UDP_PORT):
    port_pool.put(port)


def get_port():
    """Get a port from the port pool."""
    return port_pool.get()


def release_port(port):
    """Release a port back to the port pool."""
    port_pool.put(port)



def start_client():
    file_size = int(input("please input file size: "))
    tcp_conn_num = int(input("please input TCP connection number: "))
    udp_conn_num = int(input("please input UDP connection number: "))

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.bind(("", OFFER_PORT))  # Bind to the broadcast port

    print("Client started, listening for offer requests...")
    while True:
        data, server_address = udp_socket.recvfrom(CHUNK_SIZE)
        try:
            magic_cookie, message_type, server_udp_port, server_tcp_port = struct.unpack('!I B H H', data)
            if magic_cookie == EXPECTED_MAGIC_CO0KIE and message_type == OFFER_MESSAGE_TYPE:
                print(f"Received offer from {server_address[0]}")

                tcp_thread = threading.Thread(target=tcp_connection, args=(server_tcp_port, server_address[0], file_size))
                udp_thread = threading.Thread(target=udp_connection, args=(server_udp_port, server_address[0]))

                tcp_thread.start()
                udp_thread.start()

        except struct.error:
            print("Received malformed offer message.")

def tcp_connection(server_port, server_ip, file_size):
    """Handle a single TCP connection."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((server_ip, server_port))
            print(f"TCP connection established with {server_ip}:{server_port}")

            message = f"{file_size}\n"
            print(time.time())
            tcp_socket.sendall(message.encode())
            response = tcp_socket.recv(CHUNK_SIZE)
            print(f"Received from TCP server: {response.decode()}")

    except Exception as e:
        print(f"TCP connection error: {e}")


def udp_connection(server_port, server_ip):
    source_port = get_port()  # Get a port from the pool
    message_type = REQUEST_MESSAGE_TYPE
    file_size = 1234567890  # 8 bytes (example file size)

    # Pack the values into a binary structure

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.bind(('', source_port))
            print(f"UDP connection bound to port {source_port}")

            message = struct.pack('!I B Q', EXPECTED_MAGIC_CO0KIE, message_type, file_size)
            print(time.time())
            udp_socket.sendto(message, (server_ip, server_port))
            response, addr = udp_socket.recvfrom(CHUNK_SIZE)
            print(f"Received from UDP server: {response.decode()}")

    except Exception as e:
        print(f"UDP connection error: {e}")
    finally:
        release_port(source_port)  # Release the port back to the pool


if __name__ == "__main__":
    start_client()
