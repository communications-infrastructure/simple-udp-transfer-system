import socket
import threading
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
        if msg == "!DISCONNECT":
            connected = False
        print(f"[SERVER] {msg}")
    client.close()

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    connected = True
    print(f"[CONNECTED] Main Client - Connected to {IP}:{PORT}")
    client.send("!MAIN_CONN".encode(FORMAT))
    msg = client.recv(1024).decode(FORMAT)
    print(f"[SERVER] {msg}")

    while connected:
        msg = input("Enter a command: ")
        client.send(msg.encode(FORMAT))
        if msg == "!DISCONNECT":
            connected = False
        elif msg == "!START_CONN":
            for i in range(26):
                client = threading.Thread(target=connect_client, args=(i+1,))
                client.start()

        msg = client.recv(1024).decode(FORMAT)
        print(f"[SERVER] {msg}")
        

if __name__ == "__main__":
    main()