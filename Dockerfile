FROM python:3.8-slim

WORKDIR /app

COPY ./app/custom /app/custom
COPY ./app/system /app/system
COPY ./app/assets /static/assets
COPY ./app/main.py /app/main.py

COPY ./requirements.txt /app

RUN pip install -r /app/requirements.txt

CMD ["python", "/app/main.py"]
