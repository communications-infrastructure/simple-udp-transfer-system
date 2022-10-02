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
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        server.listen()
        log.info(f"[PROCESS] Server process ID: {os.getpid()}")
        log.info(f'[LISTENING] Server is listening on {IP}:{PORT}')
        current_clients = list()
        client_id = 1
        threading_condition = threading.Condition()
        while True:
            conn, addr = server.accept()
            client = Client(client_id, threading_condition)
            threaded_client = threading.Thread(
                target=client.handle_client, args=(conn, addr))
            threaded_client.daemon = True
            threaded_client.start()
            current_clients.append(client)
            client.setClientList(current_clients)
            log.info(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
            client_id += 1


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
