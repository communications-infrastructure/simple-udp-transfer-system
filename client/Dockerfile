FROM python:3

COPY client /home/client

RUN pip install -r /home/client/requirements.txt

ENTRYPOINT python3.10 /home/client/client.py