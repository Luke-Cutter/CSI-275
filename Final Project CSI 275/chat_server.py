"""Student code for CSI-275 Final Project.

Description: The chat_server.py file implements a chat server that allows
multiple clients to connect and communicate with each other. The server uses
the TCP protocol and handles client connections using threading. When a
client connects to the server, a new thread is created to handle the
communication with that specific client. The server supports various types
of messages, including broadcasting messages to all connected clients,
sending private messages to a specific recipient, and handling client join
and leave events. The server also gracefully handles connection errors and
disconnections, ensuring that the chat system remains stable and responsive.

Author: Luke Cutter
Class: CSI-275-01, Spring 2024
Assignment: Final Project
Certification of Authenticity:
I certify that this is entirely my own work, except where I have given
fully-documented references to the work of others. I understand the definition
and consequences of plagiarism and acknowledge that the assessor of this
assignment may, for the purpose of assessing this assignment:
- Reproduce this assignment and provide a copy to another member of academic
- staff; and/or Communicate a copy of this assignment to a plagiarism checking
- service (which may then retain a copy of this assignment on its database for
- the purpose of future plagiarism checking)
"""

import socket
import json
import struct
import threading


class ChatServer:
    """Create a TCP server and listen for incoming connections."""

    def __init__(self, host, port):
        """Set up the TCP server and bind it to host and port."""
        self.host = host
        self.port = port
        # Store who is currently in the server
        self.clients = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))

    def broadcast(self, message, sender):
        """Check if message is sent by client and broadcast if not."""
        for screen_name, client in self.clients.items():
            if screen_name != sender:
                client.send(message)

    def send_private(self, message, sender, recipient):
        """Send a private message from one client to another."""
        if recipient in self.clients:
            self.clients[recipient].send(message)
        # If recipient does not exist, throw an error
        else:
            error_msg = json.dumps(['ERROR', f'Recipient {recipient}'
                                             f' not found']).encode('utf-8')
            error_msg_len = len(error_msg)
            # https://docs.python.org/3/library/struct.html
            error_msg_len_bytes = struct.pack('!I', error_msg_len)
            self.clients[sender].send(error_msg_len_bytes + error_msg)

    def handle_client(self, client_sock):
        """Handle communication with a connected client."""
        client_screen_name = None
        while True:
            try:
                # Receive the message length
                msg_len_bytes = client_sock.recv(4)
                if not msg_len_bytes:
                    break
                # https://docs.python.org/3/library/struct.html
                msg_len = struct.unpack('!I', msg_len_bytes)[0]

                # Receive and decode the message data
                msg_data = client_sock.recv(msg_len).decode('utf-8')
                msg = json.loads(msg_data)

                # Process the received message based on its type
                if msg[0] == 'START':
                    # Client is joining the chat
                    client_screen_name = msg[1]
                    self.clients[client_screen_name] = client_sock
                    print(f'Client {client_screen_name} connected')

                    # Send the list of connected users to the new client
                    user_list = list(self.clients.keys())
                    user_list_msg = json.dumps(['USER_LIST', user_list]).encode('utf-8')
                    user_list_msg_len = len(user_list_msg)
                    # https://docs.python.org/3/library/struct.html
                    user_list_msg_len_bytes = struct.pack('!I', user_list_msg_len)
                    client_sock.send(user_list_msg_len_bytes + user_list_msg)

                    # Broadcast a join message to all other clients
                    join_msg = json.dumps(['JOIN', client_screen_name]).encode('utf-8')
                    join_msg_len = len(join_msg)
                    # https://docs.python.org/3/library/struct.html
                    join_msg_len_bytes = struct.pack('!I', join_msg_len)
                    self.broadcast(join_msg_len_bytes + join_msg, client_screen_name)
                elif msg[0] == 'BROADCAST':
                    # Client is sending a broadcast message
                    client_screen_name, message = msg[1], msg[2]
                    print(f'{client_screen_name}: {message}')

                    # Broadcast the message to all other clients
                    broadcast_msg = json.dumps(['BROADCAST', client_screen_name, message]).encode('utf-8')
                    broadcast_msg_len = len(broadcast_msg)
                    # https://docs.python.org/3/library/struct.html
                    broadcast_msg_len_bytes = struct.pack('!I', broadcast_msg_len)
                    self.broadcast(broadcast_msg_len_bytes + broadcast_msg, client_screen_name)
                elif msg[0] == 'PRIVATE':
                    # Client is sending a private message
                    sender, recipient, message = msg[1], msg[3], msg[2]
                    print(f'Private message from {sender} to {recipient}: {message}')

                    # Send the private message to the recipient
                    private_msg = json.dumps(['PRIVATE', sender, message]).encode('utf-8')
                    private_msg_len = len(private_msg)
                    # https://docs.python.org/3/library/struct.html
                    private_msg_len_bytes = struct.pack('!I', private_msg_len)
                    self.send_private(private_msg_len_bytes + private_msg, sender, recipient)
                elif msg[0] == 'EXIT':
                    # Client is leaving the chat
                    print(f'Client {client_screen_name} disconnected')
                    del self.clients[client_screen_name]

                    # Broadcast a leave message to all other clients
                    self.broadcast_leave_message(client_screen_name)

                    # Close the client socket and break the loop
                    client_sock.close()
                    break
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                # Handle connection errors
                if client_screen_name in self.clients:
                    print(f'Client {client_screen_name} disconnected')
                    del self.clients[client_screen_name]

                    # Broadcast a leave message to all other clients
                    self.broadcast_leave_message(client_screen_name)

                # Close the client socket and break the loop
                client_sock.close()
                break

    def broadcast_leave_message(self, client_screen_name):
        """Broadcast a leave message to all other clients."""
        leave_msg = json.dumps(['LEAVE', client_screen_name]).encode('utf-8')
        leave_msg_len = len(leave_msg)
        # https://docs.python.org/3/library/struct.html
        leave_msg_len_bytes = struct.pack('!I', leave_msg_len)
        self.broadcast(leave_msg_len_bytes + leave_msg, client_screen_name)

    def accept_connections(self):
        """Accept connection and display when connected to the server."""
        self.sock.listen()
        while True:
            client_sock, _ = self.sock.accept()
            # Log in server whenever someone enters
            print(f'Accepted connection from {client_sock.getpeername()}')
            # Make a new thread for the new client
            client_handler = threading.Thread(target=self.handle_client,
                                              args=(client_sock,))
            client_handler.start()


if __name__ == '__main__':
    server = ChatServer('127.0.0.1', 8000)
    server.accept_connections()
