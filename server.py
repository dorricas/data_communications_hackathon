import time
import socket
import struct
import threading

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 65431)
    server_socket.bind(server_address)
    server_socket.listen(1)

    print(f"Server is running on {server_address[0]}:{server_address[1]}")

    # Start the UDP broadcast thread
    udp_thread = threading.Thread(target=send_udp_broadcast, args=(12345, server_address[1]), daemon=True)
    udp_thread.start()

    try:
        while True:
            print("Waiting for a connection...")
            connection, client_address = server_socket.accept()
            try:
                print(f"Connection established with {client_address}")

                while True:
                    data = connection.recv(1024)
                    if data:
                        print(f"Received: {data.decode()}")
                        response = f"Server received: {data.decode()}"
                        connection.sendall(response.encode())
                    else:
                        print("No more data from", client_address)
                        break
            finally:
                connection.close()

    except KeyboardInterrupt:
        print("\nKeyboard interrupt, server is shutting down.")


# Function to send UDP broadcast
def send_udp_broadcast(udp_port, tcp_port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_address = ('<broadcast>', 12345)

    magic_cookie = 0xabcddcba
    message_type = 0x2

    while True:
        # Construct the offer message
        message = struct.pack('!I B H H', magic_cookie, message_type, udp_port, tcp_port)
        udp_socket.sendto(message, broadcast_address)
        print(f"Broadcasted offer message with UDP port {udp_port} and TCP port {tcp_port}")
        time.sleep(1)


if __name__ == "__main__":
    start_server()