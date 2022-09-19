import os
import signal

def kill_server():
    pid = input("Input the process ID of the server: ")
    os.kill(int(pid), signal.SIGTERM)
    print("Server killed successfully")

if __name__ == "__main__":
    kill_server()
