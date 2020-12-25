FROM node:15-buster-slim

RUN apt-get update
RUN apt-get install -y python python3-pip

COPY client /client

RUN cd /client && npm install && npm run build

# RUN python3 --version
# RUN pip3 --version


