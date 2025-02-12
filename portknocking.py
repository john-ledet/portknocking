import socket
import threading
import time

# Define the knocking sequence and main port
KNOCK_SEQUENCE = [5001, 5002, 5003] 
MAIN_PORT = 9000
TIMEOUT = 10  

knock_tracker = []  

def handle_client(client_socket):
    client_socket.send(b"Access Granted!\n")
    client_socket.close()

def listen_for_knocks():
    global knock_tracker
    while True:
        for port in KNOCK_SEQUENCE:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("0.0.0.0", port))
            sock.listen(1)
            sock.settimeout(TIMEOUT)
            try:
                conn, addr = sock.accept()
                knock_tracker.append(port)
                print(f"Knock detected on port {port} from {addr}")
                if knock_tracker == KNOCK_SEQUENCE:
                    print("Correct sequence entered! Opening main port...")
                    threading.Thread(target=start_main_server).start()
                    knock_tracker = []  # Reset after success
            except socket.timeout:
                knock_tracker = []  # Reset on timeout
            finally:
                sock.close()

def start_main_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", MAIN_PORT))
    server.listen(5)
    print(f"Main server listening on port {MAIN_PORT}...")
    while True:
        client, addr = server.accept()
        print(f"Connection received from {addr}")
        handle_client(client)

if __name__ == "__main__":
    print("Starting knock listener...")
    threading.Thread(target=listen_for_knocks).start()
