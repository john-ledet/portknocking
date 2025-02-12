import socket
import threading
import time

KNOCK_SEQUENCE = [5001, 5002, 5003]
MAIN_PORT = 9000
TIMEOUT = 10 
knock_tracker = []
knock_lock = threading.Lock() 
server_started = threading.Event()  

def handle_client(client_socket):
    """Handles incoming client connections."""
    try:
        client_socket.send(b"Access Granted!\n")
        print("Sent 'Access Granted!' to client.")
    except Exception as e:
        print(f"ERROR: Failed to handle client - {e}")
    finally:
        client_socket.close()
        
def knock_listener(port):
    """Listen on a single port for knock attempts."""
    global knock_tracker
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", port))
        sock.listen(1)
        sock.settimeout(TIMEOUT)
        print(f"Listening for knocks on port {port}...")

        while True:
            try:
                conn, addr = sock.accept()
                with knock_lock:
                    knock_tracker.append(port)
                    print(f"Knock detected on port {port} from {addr}")
                    print(f"Current knock tracker: {knock_tracker}")  # DEBUG

                    if knock_tracker == KNOCK_SEQUENCE:
                        if not server_started.is_set():
                            print(" Correct knock sequence detected! Starting main server...")
                            server_started.set()  # Prevent multiple server starts
                            threading.Thread(target=start_main_server, daemon=True).start()
                            knock_tracker.clear()
                        else:
                            print("Server already started, ignoring extra knocks.")
                    else:
                        print("Knock sequence not complete yet.")

                conn.close()
            except socket.timeout:
                with knock_lock:
                    print("Knock sequence timeout")
                    knock_tracker.clear()  # Reset sequence on timeout
            except Exception as e:
                print(f"ERROR: Knock listener on port {port} failed - {e}")

    except Exception as e:
        print(f"ERROR: Could not bind to port {port} - {e}")

def start_main_server():
    """Start the main server after correct knock sequence."""
    try:
        print("Attempting to start main server on port 9000...")  # DEBUG
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Prevent 'address already in use' errors
        server.bind(("0.0.0.0", MAIN_PORT))
        server.listen(5)
        print(f"Main server **successfully** started on port {MAIN_PORT}!")

        while True:
            try:
                client, addr = server.accept()
                print(f"Connection received from {addr}")
                handle_client(client)
            except Exception as e:
                print(f"ERROR: Failed to accept client connection - {e}")

    except Exception as e:
        print(f"ERROR: Failed to start main server - {e}")

if __name__ == "__main__":
    print("Starting knock listener...")

    # Start a separate thread for each knock port
    for port in KNOCK_SEQUENCE:
        threading.Thread(target=knock_listener, args=(port,), daemon=True).start()

    while True:
        time.sleep(1)  # Keep the main thread alive

