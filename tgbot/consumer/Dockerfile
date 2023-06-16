FROM python:3.8

RUN mkdir -p /app
RUN mkdir -p /images_storage
RUN mkdir -p /models

WORKDIR /app

RUN apt-get update && apt-get install libgl1 -y
RUN pip install -U pip requests pika
RUN pip install opencv-python numpy Pillow python-dotenv telebot psycopg2
RUN pip install torch torchaudio torchvision tqdm
RUN pip install transformers diffusers==0.14.0
RUN git clone https://github.com/cloneofsimo/lora.git
RUN sed -i 's/functools.cache/functools.lru_cache(maxsize=None)/g' /app/lora/lora_diffusion/xformers_utils.py 
RUN pip install /app/lora
RUN pip uninstall accelerate
RUN pip install accelerate==0.19.0 bitsandbytes-cuda113

EXPOSE 8081

CMD ["python", "./init.py"]


