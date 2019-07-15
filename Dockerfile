FROM molguin/gabriel-lego:latest
MAINTAINER Manuel Olguín, molguin@kth.se

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y \
    iputils-ping \
    build-essential \
    python-all \
    python2.7 \
    python-pip \
    libopencv-dev \
    python-opencv \
    python-qt4 \ 
    && apt-get clean \
    &&rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install --upgrade pip
COPY . /client/
RUN pip install -r /client/requirements.txt
RUN ln -s /client/client.py /usr/bin/gabriel_client && chmod +x /usr/bin/gabriel_client
RUN ln -s /client/ui.py /usr/bin/gabriel_client_ui && chmod +x /usr/bin/gabriel_client_ui
