FROM python:3.8

RUN mkdir -p /app
RUN mkdir -p /images_storage
RUN mkdir -p /models

WORKDIR /app

RUN apt-get update && apt-get install libgl1 -y
RUN pip install -U pip requests pika
RUN pip install opencv-python numpy Pillow python-dotenv telebot psycopg2
RUN pip install torch torchaudio torchvision tqdm accelerate
RUN pip install transformers diffusers==0.14.0
# RUN pip install git+https://github.com/huggingface/diffusers

EXPOSE 8081

CMD ["python", "./init.py"]


