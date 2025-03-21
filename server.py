# AI DECLARATION: ChatGPT o1 and o3-mini-high has been used for coding help
import socket
import threading

# Server configuration. Listens on all interfaces at port 55555
HOST = '0.0.0.0'
PORT = 55555

# Data structures to hold client info (nickname, channel). Lock is used to synchronize access to shared data
clients = {}
lock = threading.Lock()

# Function to broadcast a message to all other clients in the same channel
def broadcast(message, sender_socket, channel):
    with lock:
        # Loop through all connected clients.
        for client, info in clients.items():
            # Only send to clients in the same channel and not the sender
            if client != sender_socket and info["channel"] == channel:
                try:
                    client.send(message.encode('utf-8'))
                except Exception as e:
                    print(f"Error sending message: {e}")

# Function to send a private message to a specific client
def private_message(message, sender_socket, target_nick):
    with lock:
        target_found = False
        # Search for the client with the matching nickname
        for client, info in clients.items():
            if info["nickname"] == target_nick:
                try:
                    client.send(message.encode('utf-8'))
                    target_found = True
                except Exception as e:
                    print(f"Error sending private message: {e}")
        # If client isn't found, send an error message
        if not target_found:
            try:
                sender_socket.send(f"User '{target_nick}' not found.".encode('utf-8'))
            except Exception as e:
                print(f"Error sending error message: {e}")

# Function to handle client connection.
def handle_client(client_socket, addr):
    # Assign default nickname and channel
    with lock:
        clients[client_socket] = {"nickname": f"User{addr[1]}", "channel": "general"}
        welcome_msg = ("Welcome to the chat! Your default nickname is User{} and you are in channel 'general'.\nCommands:\n /nick <new_name>  -- change nickname\n /join <channel>  -- join channel\n /pm <nickname> <message>  -- private message\n /quit  -- disconnect\n").format(addr[1])
        client_socket.send(welcome_msg.encode('utf-8'))

    # This loop listens for messages from the connected client.
    while True:
        try:
            # Receive a message from the client.
            msg = client_socket.recv(1024).decode('utf-8')
            # If no message is received, the client has disconnected.
            if not msg:
                break
            msg = msg.strip()
            
            # Command: Change nickname
            if msg.startswith("/nick "):
                new_nick = msg.split(" ", 1)[1].strip()
                with lock:
                    old_nick = clients[client_socket]["nickname"]
                    clients[client_socket]["nickname"] = new_nick
                client_socket.send(f"Nickname changed from {old_nick} to {new_nick}\n".encode('utf-8'))
            
            # Command: Join channel
            elif msg.startswith("/join "):
                new_channel = msg.split(" ", 1)[1].strip()
                with lock:
                    old_channel = clients[client_socket]["channel"]
                    clients[client_socket]["channel"] = new_channel
                client_socket.send(f"You have joined channel '{new_channel}' (was in '{old_channel}')\n".encode('utf-8'))
            
            # Command: Private message
            elif msg.startswith("/pm "):
                parts = msg.split(" ", 2)
                if len(parts) < 3:
                    client_socket.send("Usage: /pm <nickname> <message>\n".encode('utf-8'))
                else:
                    target_nick = parts[1].strip()
                    message_body = parts[2].strip()
                    sender_nick = clients[client_socket]["nickname"]
                    # Send the private message.
                    private_message(f"[PM] {sender_nick}: {message_body}", client_socket, target_nick)
            
            # Command: Quit
            elif msg == "/quit":
                break
            
            # Regular message: broadcast to channel
            else:
                sender_nick = clients[client_socket]["nickname"]
                current_channel = clients[client_socket]["channel"]
                broadcast(f"{sender_nick}: {msg}", client_socket, current_channel)
        except Exception as e:
            print(f"Error with client {addr}: {e}")
            break

    # Cleanup on disconnect
    with lock:
        if client_socket in clients:
            print(f"Client {addr} disconnected")
            del clients[client_socket]
    client_socket.close()

# Function to start the server and listen for incoming client connections.
def start_server():
    # Create a TCP socket for the server.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on {HOST}:{PORT}")

    # Loop forever, accepting new connections.
    while True:
        client_socket, addr = server.accept()
        print(f"New connection {addr}")
        # Start a new thread for each connected client.
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
