FROM resin/rpi-raspbian:stretch as runtime 
ENV CC=gcc
RUN apt-get update && apt-get install -y python3 python3-pip python3-dev iputils-ping git gcc &&\
  update-alternatives --install /usr/bin/python python /usr/bin/python3 1 &&\
  update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

COPY . /app
WORKDIR /app

# preparing env and installing the dist
RUN python -m pip install --upgrade pip setuptools &&\
  python -m pip config set global.extra-index-url "https://www.piwheels.org/simple" &&\ 
  python -m pip install RPi.GPIO &&\
  python setup.py sdist --format=gztar && python -m pip install dist/*

VOLUME ["/data"]
VOLUME ["/etc/mbox-agent"]
CMD ["/usr/local/bin/loggerd", "server", "--file", "/etc/mbox-agent/config.ini"]
