import socket
import threading
from tqdm import tqdm
import os
import sys
import logging
import time
from hashfinder.get_hash import hash_file
from logger.logger import define_log, StreamToLogger

log = logging.getLogger("client")
IP = socket.gethostbyname(socket.gethostname())
PORT = 6969
ADDR = (IP, PORT)
FORMAT = 'utf-8'
COMMANDS = ["!DISCONNECT", "!CONFIG", "!START", "!LIST"]
num_clients = None


def setup_log():
    console_handler, file_handler = define_log()
    # Redirect stdout and stderr to log:
    sys.stdout = StreamToLogger(log, logging.INFO)
    log.addHandler(file_handler)
    log.addHandler(console_handler)
    log.setLevel(logging.DEBUG)


def connect_client(client_num):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    connected = True
    log.info(f"[CONNECTED] Client #{client_num} - Connected to {IP}:{PORT}")

    while connected:
        client.send(f"!CONNECTION {client_num}".encode(FORMAT))
        msg = client.recv(1024).decode(FORMAT)
        log.info(f"[SERVER] {msg}")
        if msg == "!DISCONNECT":
            connected = False
        elif msg == "OK":
            log.info(
                f"[CLIENT #{client_num}] Connection established waiting for file transfer")
            client.send("OK".encode(FORMAT))
            msg = client.recv(1024).decode(FORMAT)
            if "TRANSFER" in msg:
                hash = client.recv(1024).decode(FORMAT)
                file_data = msg.split(":")
                filename = f"File {client_num} " + file_data[1].rstrip()
                filesize = int(file_data[2])
                log.info(
                    f"[CLIENT #{client_num}] Receiving file {filename} with size {filesize}")
                bar = tqdm(range(
                    filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                try:
                    os.makedirs('./client/ArchivosRecibidos')
                except FileExistsError:
                    pass
                global num_clients

                with open(f"./client/ArchivosRecibidos/Cliente{client_num}-Prueba{num_clients}.mp4", "wb") as f:
                    try:
                        t1 = time.time()
                        while True:
                            data = client.recv(1024)
                            if len(data) <= 0:
                                bar.close()
                                t2 = time.time()
                                log.info(
                                    f"[CLIENT #{client_num}] File transfer time: {t2-t1} seconds")
                                break
                            bar.update(len(data))
                            f.write(data)
                    except (ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError):
                        log.error("ERROR: Connection lost")
                        connected = False
                log.info(f"[CLIENT #{client_num}] File transfer complete")
                clientHash = hash_file(
                    f"./client/ArchivosRecibidos/Cliente{client_num}-Prueba{num_clients}.mp4")
                if hash == clientHash:
                    log.info(
                        f"[CLIENT #{client_num}] File transfer successful, integrity check passed - Hashes are equal.")
                    log.info(f"File Size: {filesize} bytes")
                    log.info(f"Server Hash: {hash}")
                    log.info(f"Client Hash: {clientHash}")
                else:
                    log.info(
                        f"[CLIENT #{client_num}] File transfer successful, integrity check failed - Hashes are not equal.")
                    log.info(f"File Size: {filesize} bytes")
                    log.info(f"Server Hash: {hash}")
                    log.info(f"Client Hash: {clientHash}")

                connected = False
    client.close()


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log.info(f"[STARTING] Client is starting...")
    try:
        global ADDR
        global IP
        global PORT
        client.connect(ADDR)
    except ConnectionRefusedError:
        IP = input(
            "Local server is not running, please enter the new IP address of the server: ")
        ADDR = (IP, PORT)
        client.connect(ADDR)

    connected = True
    log.info(f"[CONNECTED] Main Client - Connected to {IP}:{PORT}")
    client.send("!MAIN_CONN".encode(FORMAT))
    msg = client.recv(1024).decode(FORMAT)
    msg = msg.split("\n")
    for i in msg:
        log.info(f"[MENU] {i}")

    threads = list()

    global num_clients
    while connected:
        msg = input("[MENU] Enter a command: ")
        if not msg in COMMANDS and not "!CONFIG" in msg:
            log.info(f"[MENU] Invalid command {msg}")
            continue
        client.send(msg.encode(FORMAT))
        msg_rcv = client.recv(1024).decode(FORMAT)
        log.info(f"[SERVER] {msg_rcv}")
        if msg == "!DISCONNECT":
            connected = False
        elif "!CONFIG" in msg and "Config set" in msg_rcv:
            num_clients = int(msg.split(':')[2])
        if msg_rcv == "File Transfer Command Started":
            for i in range(num_clients):
                client = threading.Thread(target=connect_client, args=(i+1,))
                threads.append(client)
                client.start()
            connected = False


if __name__ == "__main__":
    setup_log()
    main()
