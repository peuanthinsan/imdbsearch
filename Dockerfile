FROM python:3

WORKDIR /var/www/html

COPY ./src /var/www/html

RUN pip3 install -r requirements.txt

ENV FLASK_APP=imdbscrape.app

EXPOSE 8000

CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
