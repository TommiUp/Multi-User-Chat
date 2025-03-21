# AI DECLARATION: ChatGPT o1 and o3-mini-high has been used for coding help
import socket
import threading
import sys

# Event to signal when the client is shutting down.
shutdown = threading.Event()

# Function to receive and print messages from the server. This function runs in a separate thread.
def receive_messages(sock):
    # Keep running until the shutdown is set.
    while not shutdown.is_set():
        try:
            # Receive data from the server.
            message = sock.recv(1024).decode('utf-8')
            # If no message is received, it means the server has disconnected.
            if not message:
                print("Disconnected from server.")
                break
            # Print the received message.
            print(message)
        except Exception as e:
            # Only print error if the client is not shutting down.
            if not shutdown.is_set():
                print(f"Error: {e}")
            break
    # Close the socket after finishing.
    sock.close()

# Function to read input and send messages to server
def send_messages(sock):
    # Loop until the user types '/quit'.
    while True:
        # Read a message from the user.
        msg = input()
        try:
            # Send the message to the server.
            sock.send(msg.encode('utf-8'))
            # If '/quit', signal the shutdown and break the loop.
            if msg.strip() == "/quit":
                print("Disconnecting from server.")
                shutdown.set()  # Signal the receiver thread to exit
                break
        except Exception as e:
            # Print any error and signal shutdown.
            print(f"Error: {e}")
            shutdown.set()
            break
    # Close the socket after finishing.
    sock.close()

def main():
    # Ask the user for the server IP address.
    server_ip = input("Enter server IP address: ")
    server_port = 55555

    # Create a TCP socket.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to the server using the provided IP and port.
        sock.connect((server_ip, server_port))
    except Exception as e:
        print(f"Could not connect to server: {e}")
        return

    # Start the thread to receive messages from the server. This thread will run alongside the main thread.
    recv_thread = threading.Thread(target=receive_messages, args=(sock,))
    recv_thread.start()

    # Run the send_messages function in the main thread.
    send_messages(sock)

    # Wait for the receiver thread to finish before exiting.
    recv_thread.join()
    sys.exit()

if __name__ == "__main__":
    main()
