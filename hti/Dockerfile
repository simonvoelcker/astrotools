FROM mongo:4.2-bionic

COPY . /

RUN apt-get update
RUN apt-get install -y python3.6 python3-pip
RUN pip3 install --upgrade pip
RUN pip install -r /requirements.txt

ENV FLASK_CONFIG=production
ENV USE_SIM_PLC=true
ENV USE_WEBSOCKETS=false
ENV HMI_MODE=live
ENV ALLOW_SIM_PLC_REMOTE_CONTROL=true

ENTRYPOINT  mongod --fork --logpath /var/log/mongodb.log --logappend | python3.6 /run_app.py
