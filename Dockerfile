FROM python:3.8-slim

WORKDIR /flask-app/app

COPY ./app /flask-app/app
COPY ./requirements.txt /flask-app

RUN pip install -r /flask-app/requirements.txt

CMD ["python", "main.py"]
