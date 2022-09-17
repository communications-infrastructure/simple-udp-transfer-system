import socket
import threading
import os
import sys
import asyncio

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from classes.client_handling import Client

IP = socket.gethostbyname(socket.gethostname())
PORT = 6969
ADDR = (IP, PORT)
FORMAT = 'utf-8'
CONNECTION_DICT = {}

lock = threading.RLock()

def main():
    print("[STARTING] server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[PROCESS] Current process ID: {os.getpid()}")
    print(f'[LISTENING] Server is listening on {IP}:{PORT}')
    current_clients = list()
    client_id = 1
    condition = threading.Condition()
    while True:
        conn, addr = server.accept()
        client = Client(client_id, condition)
        threaded_client = threading.Thread(target=client.handle_client, args=(conn, addr))
        threaded_client.start()
        current_clients.append(client)
        client.setClientList(current_clients)
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        client_id += 1

if  __name__ == "__main__":
    main()
