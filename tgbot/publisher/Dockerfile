FROM python:3.8

RUN mkdir -p /app
RUN mkdir -p /images_storage

WORKDIR /app

RUN apt-get update && apt-get install libgl1 -y
RUN pip install -U pip requests pika
RUN pip install opencv-python numpy Pillow python-dotenv telebot psycopg2 tqdm

EXPOSE 8080

CMD ["python", "./server.py"]


