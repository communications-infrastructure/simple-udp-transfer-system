import socket
import threading
import os
import sys
import logging
import select
import time
from logger.logger import define_log, StreamToLogger

log = logging.getLogger("client")
IP = socket.gethostbyname(socket.gethostname())
PORT = 6969
ADDR = (IP, PORT)
FORMAT = 'utf-8'
COMMANDS = ["!DISCONNECT", "!CONFIG", "!START", "!LIST"]
MENU = "Server Commands:\n!LIST - List all the available files\n!CONFIG - Set up the server file transfer configuration\n!START - Start the file transfer to all clients\n!DISCONNECT - Disconnect from the server\n"
num_clients = None
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def setup_log():
    console_handler, file_handler = define_log()
    # Redirect stdout and stderr to log:
    sys.stdout = StreamToLogger(log, logging.INFO)
    log.addHandler(file_handler)
    log.addHandler(console_handler)
    log.setLevel(logging.DEBUG)


def connect_client(client_num):
    timeout = 5
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    log.info(f"[CONNECTED] Client #{client_num} - Connected to {IP}:{PORT}")
    try:
        os.makedirs(PROJECT_PATH+'/client/ArchivosRecibidos')
    except FileExistsError:
        pass
    client.sendto(f"TRANSFER".encode(FORMAT), ADDR)
    t1 = time.time()
    data, addr = client.recvfrom(65507)
    if data:
        with open(PROJECT_PATH + f"/client/ArchivosRecibidos/Cliente{client_num}-Prueba{num_clients}.mp4", "wb") as f:
            log.info(f"[RECEIVING] Receiving file from server...")
            receiving = True
            f.write(data)
            while receiving:
                receiving = select.select([client], [], [], timeout)[0]
                if receiving:
                    data, addr = client.recvfrom(65507)
                    f.write(data)
                else:
                    f.close()
                    receiving = False
            t2 = time.time()
            file_path = PROJECT_PATH + f'/client/ArchivosRecibidos/Cliente{client_num}-Prueba{num_clients}.mp4'
            time_taken = t2 - t1
            log.info(f"[RECEIVED] Client #{client_num} - File received")
            log.info(f"[TIME] Client #{client_num} - Time elapsed: {t2-t1} seconds")
            log.info(f"[RECEIVED] Client #{client_num} - File: {os.path.getsize(file_path)} bytes")
            log.info(f"[TRANFER SPEED] Client #{client_num} - Transfer speed: {(os.path.getsize(file_path)/1024**2)/(time_taken)} bytes/second")


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    config = False
    global num_clients
    global ADDR
    IP = input("Enter the server IP: ")
    ADDR = (IP, PORT)
    msg = MENU.split("\n")
    log.info(f"[STARTING] Client is starting...")
    for i in msg:
        log.info(f"[MENU] {i}")

    threads = list()
    connected = True

    while connected:
        msg = input("[MENU] Enter a command: ")
        if not msg in COMMANDS and not "!CONFIG" in msg:
            log.info(f"[MENU] Invalid command {msg}")
            continue
        elif msg == "!LIST":
            client.sendto("LIST".encode(FORMAT), ADDR)
            data, addr = client.recvfrom(1024)
            log.info(f"[SERVER] {data.decode(FORMAT)}")
        elif "!CONFIG" in msg and not config:
            client.sendto(msg.encode(FORMAT), ADDR)
            data, addr = client.recvfrom(1024)
            if data.decode(FORMAT) == "Config set":
                config = True
                num_clients = int(msg.split(":")[2])
            log.info(f"[SERVER] {data.decode(FORMAT)}")
        elif "!CONFIG" in msg:
            log.info("[MENU] Server already configured")
        elif "!DISCONNECT" == msg:
            sys.exit(0)
        elif "!START" == msg:
            for i in range(num_clients):
                client = threading.Thread(target=connect_client, args=(i+1,))
                threads.append(client)
                client.start()
            connected = False


if __name__ == "__main__":
    setup_log()
    main()
