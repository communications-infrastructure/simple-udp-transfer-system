import socket
import threading
from tqdm import tqdm
import os
from hashfinder.get_hash import hash_file

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
                hash = client.recv(1024).decode(FORMAT)
                file_data = msg.split(":")
                filename = f"File {client_num} " + file_data[1].rstrip()
                filesize = int(file_data[2])
                bar = tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                try:
                    os.makedirs('./client/files')
                except FileExistsError:
                    pass
                with open(f"./client/files/{filename}", "wb") as f:
                    while True:
                        data = client.recv(1024)
                        if len(data) <= 0:
                            bar.close()
                            break
                        bar.update(len(data))
                        f.write(data)
                
                print(f"[CLIENT #{client_num}] File transfer complete")
                clientHash = hash_file(f"./client/files/{filename}")
                if hash == clientHash:
                    print(f"[CLIENT #{client_num}] File transfer successful, integrity check passed - Hashes are equal.")
                    print(f"Server Hash: {hash}")
                    print(f"Client Hash: {clientHash}")
                else:
                    print(f"[CLIENT #{client_num}] File transfer successful, integrity check failed - Hashes are not equal.")
                    print(f"Server Hash: {hash}")
                    print(f"Client Hash: {clientHash}")
                
                connected = False
    client.close()

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[STARTING] Client is starting...")
    try:
        global ADDR
        global IP
        global PORT
        client.connect(ADDR)
    except ConnectionRefusedError:
        IP = input("Local server is not running, please enter the new IP address of the server: ")
        ADDR = (IP, PORT)
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