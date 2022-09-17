import os
FORMAT = 'utf-8'

class Client:
    def __init__(self, connection_id):
        self.connected = False
        self.connnection = None
        self.connnection_id = connection_id
        self.conn_type = None
        self.status = None
        self.client_num = 0

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        self.connected = True
        self.connection = conn
        config_msg = conn.recv(1024).decode(FORMAT)
        if config_msg == "!MAIN_CONN":
            conn.send("Main connection received".encode(FORMAT))
            self.conn_type = "main"
        elif "!CONNECTION" in config_msg:
            self.conn_type = "client"

        selected_file = None
        while self.connected:
            if self.conn_type == "main":
                msg = conn.recv(1024).decode(FORMAT)
                if msg == "!DISCONNECT":
                    self.connected = False
                    conn.send("Disconnected from server".encode(FORMAT))
                    print(f"[DISCONNECTED] {addr} disconnected.")
                    self.disconnectClientFromList()
                elif msg == "!LIST":
                    files = [f for f in os.listdir("./server/files") if os.path.isfile(os.path.join("./server/files", f))]
                    message = "Available files: " + ", ".join(files)
                    conn.send(message.encode(FORMAT))
                elif msg == "!SEND_FILE":
                    commands = msg.split()
                    if len(commands) != 2:
                        conn.send(f"Invalid command: {msg}".encode(FORMAT))
                    elif commands[1] not in files:
                        conn.send(f"File {commands[1]} does not exist".encode(FORMAT))
                    try:
                        self.num_clients = int(commands[2])
                        selected_file = commands[1]
                        
                    except ValueError:
                        conn.send(f"Invalid number of clients: {commands[2]}".encode(FORMAT))
                elif msg == "!GET_CLIENTS":
                    conn.send(str(self._clientList).encode(FORMAT))

            elif self.conn_type == "client":
                msg = conn.recv(1024).decode(FORMAT)
                if msg == "!DISCONNECT":
                    self.connected = False
                    conn.send("Disconnected from server".encode(FORMAT))
                    print(f"[DISCONNECTED] {addr} disconnected.")
        conn.close()

    def setClientList(self, list):
        self._clientList = list

    def disconnectClientFromList(self):
        self._clientList.remove(self)