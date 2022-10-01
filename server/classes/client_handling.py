import os
import logging
from logger.logger import exception_to_log
import asyncio
from hashfinder.get_hash import hash_file
import logging
import time
import pathlib

FORMAT = 'utf-8'
MENU = "Server Commands:\n!LIST - List all the available files\n!CONFIG - Set up the server file transfer configuration\n!START - Start the file transfer to all clients\n!DISCONNECT - Disconnect from the server\n"
log = logging.getLogger('TCPServer')

class Client:
    def __init__(self, connection_id, threading_condition):
        self.connected = False
        self._connnection = None
        self.address = None
        self.connection_id = connection_id
        self.conn_type = None
        self.status = None
        self.condition = threading_condition
        self.selected_file = None
        self.num_clients = 0

    def handle_client(self, conn, addr):
        log.info(f"[NEW CONNECTION] {addr} connected.")
        self.connected = True
        self._connection = conn
        self.address = addr
        config_msg = conn.recv(1024).decode(FORMAT)
        if config_msg == "!MAIN_CONN":
            self.send(("Main connection received\n"+MENU))
            log.info(f"[MAIN CONNECTION] {addr} connected.")
            self.conn_type = "main"
        elif "!CONNECTION" in config_msg:
            self.conn_type = "client"
            self.send("OK")
        while self.connected:
            try:
                if self.conn_type == "main":
                   self.main_client()       
                elif self.conn_type == "client":
                    self.normal_client()
            except Exception as e:
                try:
                    self.send("Internal Server Error")
                except ConnectionResetError:
                    pass
                exception_to_log(log, e)
        self._connection.close()

    def send(self, msg, log_msg=False):
        self._connection.send(msg.encode(FORMAT))
        if log_msg:
            log.info(f"[FILE TRANSFER] - {msg}")

    def main_client(self):
        msg = self._connection.recv(1024).decode(FORMAT)
        try:
            files = [f for f in os.listdir("./server/files") if os.path.isfile(os.path.join("./server/files", f))]
        except FileNotFoundError:
            try:
                files = [f for f in os.listdir("/home/server/files") if os.path.isfile(os.path.join("/home/server/files", f))]
            except FileNotFoundError:
                log.critical(f"No files found in server/files or files. Current path {pathlib.Path(__file__).resolve()}")
        if msg == "!DISCONNECT":
            self.connected = False
            self.send("Disconnected from server")
            log.info(f"[DISCONNECTED] {self.address} disconnected.")
            self.disconnectClientFromList()
        elif msg == "!LIST":
            self.send(str(files))
        elif "!CONFIG" in msg and (self.selected_file == None or self.num_clients == 0):
            commands = msg.split(':')
            if len(commands) == 1:
                self.send("Invalid config format (Empty config). Please use the following format: !CONFIG :<file> :<num_clients>")
            elif len(commands) != 3:
                msg_str = ""
                for string in commands:
                    msg_str += string + " "
                self.send(f"Invalid config format! {msg_str}. Please use the following format: !CONFIG :<file> :<num_clients>")
                return
            elif commands[1].rstrip() not in files:
                self.send(f"File {commands[1]} does not exist")
                return
            try:
                self.num_clients = int(commands[2])
                self.selected_file = commands[1]
                self.send(f"Config set to {commands[1]} and {commands[2]} clients")
                log.info(f"[FILE CONFIG] File to be sent: {commands[1]}")
                filesize = os.path.getsize(f'./server/files/{self.selected_file}')
                log.info(f"[FILE CONFIG] File size: {filesize} bytes")
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
                self.send("File Transfer Command Started", log_msg=True)
                while (len(self._clientList) <= self.num_clients):
                    asyncio.run(asyncio.sleep(1))
                for client in self._clientList:
                    if client.conn_type == "client":
                        client.selected_file = self.selected_file
                self.condition.acquire()
                self.condition.notify_all()
                self.condition.release()
                self.connected = False # Disconnect the main client
        else:
            self.send("Invalid command\n"+MENU)

    def normal_client(self):
        msg = self._connection.recv(1024).decode(FORMAT)
        if msg == "!DISCONNECT":
            self.connected = False
            self.send("Disconnected from server")
            log.info(f"[DISCONNECTED] {self.address} disconnected.")
        elif msg == "OK":
            self.status = "OK"
            self.condition.acquire()
            self.condition.wait()
            self.condition.release()
            self.send(f"TRANSFER :{self.selected_file}:{os.path.getsize(f'./server/files/{self.selected_file}')}")
            file_hash = hash_file(f'./server/files/{self.selected_file}')
            with open(f"./server/files/{self.selected_file}", "rb") as f:
                data = f.read()
            self.send(f"{file_hash}")
            try:
                t1 = time.time()
                self._connection.sendall(data)
                t2 = time.time()
                log.info(f"[FILE TRANSFER] - File {self.selected_file} sent to {self.address} [CLIENT {self.connection_id}] in {t2-t1} seconds")
                self.connected = False
                log.info("File succesfully sent to Client " + str(self.connection_id))
            except (ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError):
                log.error("Error sending file to Client " + str(self.connection_id))


    def setClientList(self, list):
        self._clientList = list

    def disconnectClientFromList(self):
        self._clientList.remove(self)