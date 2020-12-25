FROM node:15-buster-slim

RUN apt-get update
RUN apt-get install -y python python3-pip libindi-dev swig python-setuptools python-dev libz-dev libnova-dev influxdb

COPY hti /hti
COPY lib /lib

RUN pip3 install -r /hti/requirements.txt

RUN cd /hti/client && npm install && npm run build


ENV SIM_CAMERA=true
ENV SIM_AXES=true
ENV PYTHONPATH=/

ENTRYPOINT python3 /hti/run_server.py
