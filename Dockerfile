FROM python:2.7

MAINTAINER Aaron Barnes <aaron@io.net.nz>

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python-pip libmysqld-dev python-dev libcurl4-openssl-dev
RUN pip install virtualenv

ADD requirements.txt /tmp/

RUN mkdir /code

RUN cd /code && \
    virtualenv . && \
    bin/pip install -r /tmp/requirements.txt

ADD . /code/

RUN adduser --system --no-create-home --disabled-login jarvis

EXPOSE 4188

USER jarvis

WORKDIR /code

CMD ["./start_server.py"]
