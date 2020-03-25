#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""

from threading import Thread, current_thread
import socket
from googletrans import Translator
from langdetect import detect
from models.user import User
import json

translator = Translator()


    
def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Welcome Shitty Chat App! Type your username and press enter!", "utf8"))
        addresses[client] = client_address
        print('Connection Thread', current_thread().name)
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.


    print('Handle Thread', current_thread().name)
        

    """Handles a single client connection."""
    
    username = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % username
    client.send(bytes(welcome, "utf8"))
    
    user_obj = User(username,client)
    
    msg = "%s has joined the chat!" % username
    broadcast(bytes(msg, "utf8"))
    clients[username] = user_obj
    print(clients)  
    print(f'{user_obj.username} mapped to {client}')
    while True:
        msg = client.recv(BUFSIZ)
        user=clients[username]
        decoded_msg= msg.decode('utf8')


        if decoded_msg.startswith('!changelanguage'):
            language= decoded_msg.split()[1]
            print(f'updating language for {user.username} to {language}')

            user.update_language_pref(language)
            print(f'Update Successful.')
            continue

            

        #check if command is written

        if msg != bytes("{quit}", "utf8"):
            language=clients[username].language
            broadcast(msg, username,language)
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % username, "utf8"))
            break


def broadcast(msg, sender="",sender_language=""):  # sender is for username identification.
    
    def try_translate(msg,language):
        try:
            result = translator.translate(msg, dest=language)
            return result.text
        except ValueError:
            return None

        

    """Broadcasts a message to all the clients."""

    for username, user in clients.items():
        if user.language != sender_language:          #check if user has changed their language settings
            translated_msg = try_translate(msg.decode('utf8'), user.language)
            if translated_msg:
                outgoing_msg=translated_msg.encode('utf8')
        else:
            outgoing_msg=msg

        if not sender:    #server speaking
            user.client_info.send(bytes(sender, "utf8")+outgoing_msg) 
        
        elif user.username in sender:
            user.client_info.send(bytes('You: ', "utf8")+msg)   #post the raw message to the senders screen
        else:
            user.client_info.send(bytes(f'{sender}: ', "utf8")+outgoing_msg)  #post the translated message to receivers

        
clients = {}
addresses = {}


HOST = ''
PORT = 33008
BUFSIZ = 10000
ADDR = (HOST, PORT)

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5000)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()