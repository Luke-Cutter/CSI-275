"""Student code for CSI-275 Final Project.

Description: The chat_client.py file implements a client-side application that
allows users to connect to a chat server and participate in real-time
communication with other connected clients. The client handles various types
of messages and events. When the client is started, it prompts the user to
enter a screen name, which serves as their identifier in the chat room. The
client then establishes a connection to the specified chat server using the
provided host and port information. Once connected, the client creates a
separate thread for receiving messages from the server. This thread
continuously listens for incoming messages and processes them based on
their type. The client supports handling broadcast messages, private messages,
join and leave announcements, and error messages. The main thread of the
client handles user input and sends messages to the server. Users can send
broadcast messages to all connected clients by simply typing their message and
pressing enter. They can also send private messages to a specific recipient by
using the "@" symbol followed by the recipient's screen name. The client
provides a convenient way to exit the chat by typing "!exit" as a message.

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


class ChatClient:
    """A client for connecting to a chat server and exchanging messages."""

    def __init__(self, server_host, server_port, screen_name):
        """Initialize ChatClient with server host, port, and screen name."""
        self.server_host = server_host
        self.server_port = server_port
        self.screen_name = screen_name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_host, self.server_port))
        self.connected = True

    def send_message(self, msg_type, message, recipient=None):
        """Send a message to the chat server."""
        msg = ""
        if msg_type == 'START':
            # Create a START message with the client's screen name
            msg = json.dumps(['START', self.screen_name])
        elif msg_type == 'BROADCAST':
            # Create a BROADCAST message with
            # the client's screen name and message
            msg = json.dumps(['BROADCAST', self.screen_name, message])
        elif msg_type == 'PRIVATE':
            # Create a PRIVATE message with the client's
            # screen name, message, and recipient
            msg = json.dumps(['PRIVATE', self.screen_name, message,
                              recipient])
        elif msg_type == 'EXIT':
            # Create an EXIT message with the client's screen name
            msg = json.dumps(['EXIT', self.screen_name])

        # Encode the message and send it to the server
        msg_bytes = msg.encode('utf-8')
        msg_len = len(msg_bytes)
        # https://docs.python.org/3/library/struct.html
        msg_len_bytes = struct.pack('!I', msg_len)
        self.sock.send(msg_len_bytes + msg_bytes)

        if msg_type == 'EXIT':
            # If the message is an EXIT message,
            # close the socket and set connected to False
            self.connected = False
            self.sock.close()

    def receive_messages(self):
        """Receive and process messages from the chat server."""
        # Send a START message to the server to indicate the client has joined
        self.send_message('START', None)
        while self.connected:
            try:
                # Receive the message length
                msg_len_bytes = self.sock.recv(4)
                if not msg_len_bytes:
                    break
                # https://docs.python.org/3/library/struct.html
                msg_len = struct.unpack('!I', msg_len_bytes)[0]

                # Receive the message data
                msg_data = self.sock.recv(msg_len).decode('utf-8')
                msg = json.loads(msg_data)

                # Process the received message based on its type
                if msg[0] == 'BROADCAST':
                    # Display a broadcast message
                    sender, message = msg[1], msg[2]
                    print(f"{sender}: {message}")
                elif msg[0] == 'PRIVATE':
                    # Display a private message
                    sender, message = msg[1], msg[2]
                    print(f"{sender} (private): {message}")
                elif msg[0] == 'JOIN':
                    # Display a join message when a client joins the chat
                    screen_name = msg[1]
                    print(f"{screen_name} has joined the chat")
                elif msg[0] == 'LEAVE':
                    # Display a leave message when a client leaves the chat
                    screen_name = msg[1]
                    print(f"{screen_name} has left the chat")
                elif msg[0] == 'USER_LIST':
                    # Receive the list of connected users
                    user_list = msg[1]
                    print("Connected users:")
                    for user in user_list:
                        print(user)
                elif msg[0] == 'ERROR':
                    # Display an error message
                    print(f"Error: {msg[1]}")

                # Display the prompt for the next message
                print("> ", end="", flush=True)
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                # Handle connection errors
                print('Disconnected from the server')
                self.connected = False
                break

    def start(self):
        """Start the chat client and handle user input."""
        # Create a separate thread for receiving messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        try:
            while self.connected:
                # Read user input
                message = input("> ")

                if message.startswith("@"):
                    # If the message starts with "@", it's a private message
                    recipient, message = message.split(" ", 1)
                    recipient = recipient[1:]
                    self.send_message('PRIVATE', message, recipient)
                elif message == "!exit":
                    # If the message is "!exit", send an EXIT message
                    # and break the loop
                    self.send_message('EXIT', None)
                    break
                else:
                    # Otherwise, send a broadcast message
                    self.send_message('BROADCAST', message)
        except KeyboardInterrupt:
            # Handle keyboard interrupt (Ctrl+C) and send an EXIT message
            self.send_message('EXIT', None)
        finally:
            # Wait for the receiving thread to finish and close the socket
            receive_thread.join()
            self.sock.close()


if __name__ == '__main__':
    client_screen_name = input("Enter your screen name: ")
    client = ChatClient('127.0.0.1', 8000, client_screen_name)
    client.start()
