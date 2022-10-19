from logger.logger import define_log, StreamToLogger
from classes.client_handling import Client
import socket
import threading
import os
import sys
import logging

log = logging.getLogger('TCPServer')

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
        config = None
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(ADDR)
        log.info(f"[PROCESS] Server process ID: {os.getpid()}")
        log.info(f'[LISTENING] Server is listening on {IP}:{PORT}')
        while True:
            data, addr = server.recvfrom(1024)
            data = data.decode(FORMAT)
            log.info(f"[RECEIVED] Received data from client: {data}")
            if "LIST" == data:
                path = PROJECT_PATH + "/files"
                if not "/server" in path:
                    path = PROJECT_PATH + "/server/files"
                server.sendto(str(files).encode(FORMAT), addr)
            elif "CONFIG" in data:
                commands = data.split(':')
                if len(commands) == 1:
                    server.sendto("Invalid config format (Empty config). Please use the following format: !CONFIG :<file>".encode(FORMAT), addr)
                elif len(commands) != 3:
                    msg_str = ""
                    for string in commands:
                        msg_str += string + " "
                    server.sendto(f"Invalid config format! {msg_str}. Please use the following format: !CONFIG :<file> :<num_clients>".encode(FORMAT), addr)
                    return
                elif commands[1].rstrip() not in files:
                    server.send(f"File {commands[1].rstrip()} does not exist".encode(FORMAT), addr)
                    return
            elif "TRANSFER" == data:
                pass

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
