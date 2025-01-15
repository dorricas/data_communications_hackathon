import time
import socket
import struct
import threading


TCP_PORT = 65431
UDP_PORT = 65430
OFFER_PORT = 12345

BROADCAST = '<broadcast>'
LOCALHOST = "localhost"
ALL_NETWORK_IP ="0.0.0.0"

def start_server():
    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_address = ('localhost', OFFER_PORT)
    # server_socket.bind(server_address)
    # server_socket.listen(1)
    #
    # print(f"Server is running on {server_address[0]}:{server_address[1]}")
    #
    # # Start the UDP broadcast thread
    # udp_thread = threading.Thread(target=send_udp_broadcast, args=(UDP_PORT, TCP_PORT), daemon=True)
    # udp_thread.start()
    #
    # send_udp_broadcast()
    #
    # try:
    #     while True:
    #         print("Waiting for a connection...")
    #         connection, client_address = server_socket.accept()
    #         try:
    #             print(f"Connection established with {client_address}")
    #
    #             while True:
    #                 data = connection.recv(1024)
    #                 if data:
    #                     print(f"Received: {data.decode()}")
    #                     response = f"Server received: {data.decode()}"
    #                     connection.sendall(response.encode())
    #                 else:
    #                     print("No more data from", client_address)
    #                     break
    #         finally:
    #             connection.close()
    #
    # except KeyboardInterrupt:
    #     print("\nKeyboard interrupt, server is shutting down.")

    offer_thread = threading.Thread(target=send_udp_broadcast, args=(UDP_PORT, TCP_PORT), daemon=True)
    offer_thread.start()

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((ALL_NETWORK_IP, TCP_PORT))
    tcp_socket.listen(1)  # Backlog of 5 connections
    print(f"TCP server is listening on {ALL_NETWORK_IP}:{TCP_PORT}")

    # UDP socket setup
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((LOCALHOST, UDP_PORT))
    print(f"UDP server is listening on {LOCALHOST}:{UDP_PORT}")

    # Start threads for each protocol
    tcp_thread = threading.Thread(target=handle_tcp_connections, args=(tcp_socket,), daemon=True)
    udp_thread = threading.Thread(target=handle_udp_connections, args=(udp_socket,), daemon=True)

    tcp_thread.start()
    udp_thread.start()

    try:
        # Keep the main thread alive to allow background threads to run
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        # tcp_socket.close()
        # udp_socket.close()


# Function to send UDP broadcast
def send_udp_broadcast(udp_port, tcp_port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_address = (BROADCAST, OFFER_PORT)

    magic_cookie = 0xabcddcba
    message_type = 0x2

    while True:
        # Construct the offer message
        message = struct.pack('!I B H H', magic_cookie, message_type, udp_port, tcp_port)
        udp_socket.sendto(message, broadcast_address)
        print(f"Broadcasted offer message with UDP port {udp_port} and TCP port {tcp_port}")
        time.sleep(1)


    # udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # broadcast_address = ('<broadcast>', 12345)
    #
    # magic_cookie = 0xabcddcba
    # message_type = 0x2
    #
    # while True:
    #     # Construct the offer message
    #     message = struct.pack('!I B H H', magic_cookie, message_type, udp_port, tcp_port)
    #     udp_socket.sendto(message, broadcast_address)
    #     print(f"Broadcasted offer message with UDP port {udp_port} and TCP port {tcp_port}")
    #     time.sleep(1)

def handle_tcp_connections(tcp_socket):
    """Handle incoming TCP connections."""
    try:
        while True:
            print("Waiting for a TCP connection...")
            connection, client_address = tcp_socket.accept()
            print(f"TCP connection established with {client_address}")
            # threading.Thread(target=handle_single_tcp_client, args=(connection, client_address), daemon=True).start()

            data = connection.recv(1024)
            if data:
                print(f"Received from TCP client {client_address}: {data.decode()}")
                response = f"Server received: {data.decode()}"
                connection.sendall(response.encode())
            else:
                print(f"TCP client {client_address} disconnected.")
                break
    except Exception as e:
        print(f"Error in TCP handler: {e}")


def handle_single_tcp_client(connection, client_address):
    """Handle communication with a single TCP client."""
    try:
        with connection:
            while True:
                data = connection.recv(1024)
                if data:
                    print(f"Received from TCP client {client_address}: {data.decode()}")
                    response = f"Server received: {data.decode()}"
                    connection.sendall(response.encode())
                else:
                    print(f"TCP client {client_address} disconnected.")
                    break
    except Exception as e:
        print(f"Error with TCP client {client_address}: {e}")


def handle_udp_connections(udp_socket):
    """Handle incoming UDP messages."""
    try:
        while True:
            data, client_address = udp_socket.recvfrom(1024)
            print(f"Received from UDP client {client_address}: {data.decode()}")
            response = f"Server received: {data.decode()}"
            udp_socket.sendto(response.encode(), client_address)
    except Exception as e:
        print(f"Error in UDP handler: {e}")



if __name__ == "__main__":
    start_server()