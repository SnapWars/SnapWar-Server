FROM python:3.8-slim

WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN apt-get -qq update -y
RUN apt-get install -y python-pip

RUN pip install -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080
ENTRYPOINT ["python", "app.py"]
