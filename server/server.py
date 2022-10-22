from logger.logger import define_log, StreamToLogger
import socket
import threading
import os
import sys
import logging
import time

log = logging.getLogger('UDPServer')

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

IP = socket.gethostbyname(socket.gethostname())
PORT = 6969
ADDR = (IP, PORT)
FORMAT = 'utf-8'
CONNECTION_DICT = {}
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def setup_log():
    console_handler, file_handler = define_log()
    # Redirect stdout and stderr to log:
    sys.stdout = StreamToLogger(log, logging.INFO)
    sys.stderr = StreamToLogger(log, logging.ERROR)
    log.addHandler(file_handler)
    log.addHandler(console_handler)
    log.setLevel(logging.DEBUG)


class SocketListener(threading.Thread):

    def run(self):
        self.start_server()

    def start_server(self):
        # Server Variables
        file_to_be_sent = None
        self.path = PROJECT_PATH + "/files"
        if not "/server" in self.path:
            self.path = PROJECT_PATH + "/server/files"
        files = [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]

        # Server config
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(ADDR)
        log.info(f"[PROCESS] Server process ID: {os.getpid()}")
        log.info(f'[LISTENING] Server is listening on {IP}:{PORT}')
        while True:
            data, addr = self.server.recvfrom(1024)
            data = data.decode(FORMAT)
            log.info(f"[RECEIVED] Received data from client: {data}")
            if "LIST" == data:
                self.server.sendto(str(files).encode(FORMAT), addr)
            elif "CONFIG" in data:
                commands = data.split(':')
                if len(commands) == 1 or len(commands) == 0:
                    self.server.sendto("Invalid config format (Empty config). Please use the following format: !CONFIG :<file>".encode(FORMAT), addr)
                elif len(commands) != 3:
                    msg_str = ""
                    for string in commands:
                        msg_str += string + " "
                    self.server.sendto(f"Invalid config format! {msg_str}. Please use the following format: !CONFIG :<file> :<num_clients>".encode(FORMAT), addr)
                elif commands[1].rstrip() not in files:
                    self.server.sendto(f"File {commands[1].rstrip()} does not exist".encode(FORMAT), addr)
                else:
                    file_to_be_sent = commands[1].rstrip()
                    self.server.sendto("Config set".encode(FORMAT), addr)
            elif "TRANSFER" == data:
                thread = threading.Thread(target=self.send_file, args=(file_to_be_sent, addr))
                thread.start()

    def send_file(self, file_to_be_sent, addr):
        with open(self.path + '/' + file_to_be_sent, 'rb') as f:
            log.info(f"[TRANSFER] Sending file {file_to_be_sent} to client {addr}")
            log.info(f"[TRANSFER] File size: {os.path.getsize(self.path + '/' + file_to_be_sent)} bytes. Client {addr}")
            t1 = time.time()
            data = f.read(65507)
            while data:
                if self.server.sendto(data, addr):
                    data = f.read(65507)
            t2 = time.time()
        log.info(f"[TRANSFER] File {file_to_be_sent} sent to client {addr}")
        log.info(f"[TRANSFER] Time taken to send file: {t2 - t1} seconds. Client {addr}")


def main():
    log.info("[STARTING] server is starting...")
    pid = os.getpid()
    server_listener = SocketListener()
    server_listener.start()
    try:
        input("[MAIN THREAD] Press Enter to exit...")
        log.info(f"[MAIN THREAD] Server is stopping...")
        os.kill(pid, 9)
    except EOFError:
        pass
    except KeyboardInterrupt:
        log.info(f"[MAIN THREAD] Server is stopping...")
        os.kill(pid, 9)


if __name__ == "__main__":
    setup_log()
    main()
