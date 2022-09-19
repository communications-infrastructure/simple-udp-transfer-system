import os
import logging
from logger.logger import exception_to_log
import asyncio

FORMAT = 'utf-8'
MENU = "Server Commands:\n!LIST - List all the available files\n!CONFIG - Set up the server file transfer configuration\n!START - Start the file transfer to all clients\n!DISCONNECT - Disconnect from the server\n"
log = logging.getLogger('TCPServer')

class Client:
    def __init__(self, connection_id, threading_condition):
        self.connected = False
        self.connnection = None
        self.address = None
        self.connection_id = connection_id
        self.conn_type = None
        self.status = None
        self.condition = threading_condition

    def handle_client(self, conn, addr):
        log.info(f"[NEW CONNECTION] {addr} connected.")
        self.connected = True
        self.connection = conn
        self.address = addr
        config_msg = conn.recv(1024).decode(FORMAT)
        if config_msg == "!MAIN_CONN":
            self.send(("Main connection received\n"+MENU))
            self.conn_type = "main"
        elif "!CONNECTION" in config_msg:
            self.conn_type = "client"
        self.selected_file = None
        self.num_clients = 0
        while self.connected:
            try:
                if self.conn_type == "main":
                   self.main_client()           
                elif self.conn_type == "client":
                    self.normal_client()
            except Exception as e:
                self.send("Internal Server Error")
                exception_to_log(log, e)
        self.connection.close()

    def send(self, msg, log=False):
        self.connection.send(msg.encode(FORMAT))
        if log:
            log.info(f"[FILE TRANSFER] - {msg}")

    def main_client(self):
        msg = self.connection.recv(1024).decode(FORMAT)
        files = [f for f in os.listdir("./server/files") if os.path.isfile(os.path.join("./server/files", f))]
        if msg == "!DISCONNECT":
            self.connected = False
            self.send("Disconnected from server")
            log.info(f"[DISCONNECTED] {self.address} disconnected.")
            self.disconnectClientFromList()
        elif msg == "!LIST":
            self.send(str(files))
        elif "!CONFIG" in msg and (self.selected_file == None or self.num_clients == 0):
            commands = msg.split()
            if len(commands) == 1:
                self.send("Invalid cPlease use the following format: !CONFIG <file> <num_clients>onfig format (Empty config). Please use the following format: !CONFIG <file> <num_clients>")
            elif len(commands) != 3:
                msg_str = ""
                for string in commands:
                    msg_str += string + " "
                self.send(f"Invalid config format! {msg_str}. Please use the following format: !CONFIG <file> <num_clients>")
                return
            elif commands[1] not in files:
                self.send(f"File {commands[1]} does not exist")
                return
            try:
                self.num_clients = int(commands[2])
                self.selected_file = commands[1]
            except ValueError:
                self.send(f"Invalid number of clients: {commands[2]}")
        elif msg == "!CONFIG":
            self.send(f"Config already set up\nFile: {self.selected_file}\nNumber of clients: {self.num_clients}")
        elif msg == "!GET_CLIENTS":
            self.send(str(self._clientList))
        elif msg == "!START":
            if not self.selected_file or self.num_clients == 0:
                self.send("The settings have not been set. You need to configure the server in order to start")
            else:
                self.send("File Transfer Command Started", log=True)
                while (len(self._clientList) != self.num_clients):
                    asyncio.run(asyncio.sleep(1))
                self.condition.notify_all()
        else:
            self.send("Invalid command\n"+MENU)

    def normal_client(self):
        msg = self.connection.recv(1024).decode(FORMAT)
        if msg == "!DISCONNECT":
            self.connected = False
            self.send("Disconnected from server")
            log.info(f"[DISCONNECTED] {self.address} disconnected.")
        elif msg == "OK":
            self.status = "OK"
            self.condition.wait()
            ## TODO: Send file to client
            self.send("OK")


    def setClientList(self, list):
        self._clientList = list

    def disconnectClientFromList(self):
        self._clientList.remove(self)