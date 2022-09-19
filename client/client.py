import socket
import threading
from tkinter.tix import FileEntry
from tqdm import tqdm
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 6969
ADDR = (IP, PORT)
FORMAT = 'utf-8'

def connect_client(client_num):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    connected = True
    print(f"[CONNECTED] Client #{client_num} - Connected to {IP}:{PORT}")

    while connected:
        client.send(f"!CONNECTION {client_num}".encode(FORMAT))
        msg = client.recv(1024).decode(FORMAT)
        print(f"[SERVER] {msg}")
        if msg == "!DISCONNECT":
            connected = False
        elif msg == "OK":
            print(f"[CLIENT #{client_num}] Connection established waiting for file transfer")
            client.send("OK".encode(FORMAT))
            msg = client.recv(1024).decode(FORMAT)
            if "TRANSFER" in msg:
                file_data = msg.split(":")
                filename = file_data[1].rstrip()
                filesize = int(file_data[2])
                bar = tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                try:
                    os.makedirs('./client/files')
                except FileExistsError:
                    pass
                client.settimeout(5)
                try:
                    with open(f"./client/files/{filename}", "wb") as f:
                        while True:
                            data = client.recv(1024)
                            bar.update(len(data))
                            if not data:
                                break
                            f.write(data)
                except TimeoutError:
                    if os.path.getsize(f"./client/files/{filename}") == filesize:
                        print(f"[CLIENT #{client_num}] File transfer complete")
                connected = False
    client.close()

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    connected = True
    print(f"[CONNECTED] Main Client - Connected to {IP}:{PORT}")
    client.send("!MAIN_CONN".encode(FORMAT))
    msg = client.recv(1024).decode(FORMAT)
    print(f"[SERVER] {msg}")

    threads = list()

    num_clients = None
    while connected:
        msg = input("Enter a command: ")
        client.send(msg.encode(FORMAT))
        msg_rcv = client.recv(1024).decode(FORMAT)
        print(f"[SERVER] {msg_rcv}")
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
    main()