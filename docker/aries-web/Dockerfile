FROM python:3.6

MAINTAINER Ilya Sychev "ilya.sychev@tu-dresden.de"

RUN apt-get update \
    && apt-get install -y nginx

ADD ./ /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements/dev.txt
RUN pyb
RUN pip install /app/target/dist/aries-0.1/dist/aries-0.1.tar.gz

# Install uWSGI
RUN pip install uwsgi
RUN mkdir -p /etc/uwsgi
COPY docker/uwsgi.ini /etc/uwsgi/


# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log
EXPOSE 80 443


# Make NGINX run on the foreground
# RUN echo "daemon off;" >> /etc/nginx/nginx.conf
# Copy the modified Nginx conf
COPY docker/nginx.conf /etc/nginx/

## Install Supervisord
RUN apt-get install -y supervisor
## Custom Supervisord config
COPY docker/supervisord.conf /etc/supervisord.conf

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]