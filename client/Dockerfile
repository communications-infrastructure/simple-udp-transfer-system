FROM python:3

COPY client /home/client
COPY requirements.txt /home/client/requirements.txt

RUN pip install --upgrade pip && pip install -r /home/client/requirements.txt

ENTRYPOINT python3.10 /home/client/client.py