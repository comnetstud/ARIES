FROM python:3.6

MAINTAINER Ilya Sychev "ilya.sychev@tu-dresden.de"

ADD ./ /app
WORKDIR /app

RUN pip install -r requirements/dev.txt
RUN pyb
RUN pip install /app/target/dist/aries-0.1/dist/aries-0.1.tar.gz
