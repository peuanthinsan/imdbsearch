FROM python:3

RUN apt-get update && \
    apt-get install -y

COPY ./src /var/www/html

RUN pip3 install -r /var/www/html/requirements.txt

WORKDIR /var/www/html
ENV FLASK_APP=imdbscrape.app

EXPOSE 8000
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
