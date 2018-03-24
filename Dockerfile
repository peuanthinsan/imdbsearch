FROM python:3

RUN apt-get update && \
    apt-get install -y && \
    pip3 install uwsgi

COPY ./src /var/www/html

RUN pip3 install -r /var/www/html/requirements.txt

EXPOSE 8000
CMD uwsgi --ini /var/www/html/uwsgi.ini
