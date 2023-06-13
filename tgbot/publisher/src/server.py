from Modules.Publisher import Publisher

import warnings
warnings.filterwarnings("ignore")

from datetime import datetime
import time
import telebot
from telebot import types
import logging
import os

from dotenv import load_dotenv
load_dotenv()


bot = telebot.TeleBot(os.getenv("TELEGRAM_API_TOKEN"))
time.sleep(15)


@bot.message_handler(commands=['start', 'menu'])
def start(message):
    text = 'Привет! Я - бот, который умеет обучать ControlNet и LoRA на твоих данных'
    text += ', а потом генерировать изображения по текстовому запросу в определенном стиле.\n\n'
    text += 'Мои команды:\n'
    text += '/controlnet - загружаешь фото и промпт, ждешь меньше минуты, получаешь сгенерированное изображение'
    text += '\n/lora_train - загружаешь несколько фото, ждешь около 10-15 минут, а затем генерируешь фото с помощью'
    text += ' команды /lora_gen'
    text += '\n/lora_gen - генерация изображений на основе последней обученной нейронной сети'
    text += '\n/lora_list - получить список обученных моделей'
    text += '\n/lora_gen/{model_id} - сгенерировать изображение на основе модели по ее идентификатору'
    text += '\n/stats - статистика использования сервиса'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('/menu')
    markup.add(btn)

    bot.send_message(message.from_user.id, text, reply_markup = markup)


@bot.message_handler(commands=['controlnet'])
def start(message):
    text = '''
    Пришли мне изображение хорошего качества.
    '''
    msg = bot.send_message(message.from_user.id, text)
    bot.register_next_step_handler(msg, get_controlnet_photo)


def get_controlnet_photo(message):
    if message.content_type == 'photo':
        raw = message.photo[2].file_id
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)

        path_to_image_dir = os.path.join('/', 'images_storage', 'ControlNet', str(message.from_user.id))
        if not os.path.exists(path_to_image_dir):
            os.mkdir(path_to_image_dir)

        img_name = str(int(datetime.now().timestamp())) + ".jpg"
        path_to_image = os.path.join(path_to_image_dir, img_name)

        with open(path_to_image,'wb') as new_file:
            new_file.write(downloaded_file)

        text = 'Супер, фото я загрузил. Теперь ты можешь либо сразу выбрать готовый стиль из списка, либо сам написать промпт.'
        text += ' Например: a close up photo of a woman. Дальше я сам дополню твой промпт'
        text += ' "магическими" фразами, чтобы улучшить качество генерации, так что no worries, как говорится :)'

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        btns = []
        btns.append(types.KeyboardButton('Fantasy'))
        btns.append(types.KeyboardButton('Realistic'))
        btns.append(types.KeyboardButton('The Witcher'))
        btns.append(types.KeyboardButton('Cyberpank'))

        markup.add(*btns)

        msg = bot.send_message(message.from_user.id, text, reply_markup = markup)
        bot.register_next_step_handler(msg, get_controlnet_prompt, path_to_image_dir, img_name)
    else:
        text = 'Эй, ну ты чего, это же не фотка. Загрузи именно изображение плз и не в виде файла :)'
        msg = bot.send_message(message.from_user.id, text)
        bot.register_next_step_handler(msg, get_controlnet_photo)


def get_controlnet_prompt(message, path_to_image_dir, img_name):
    if message.content_type == 'text':
        bot.send_message(message.from_user.id, 
                         'Всё хорошо. Ставлю генерацию в очередь...', 
                         reply_markup = types.ReplyKeyboardRemove())

        publisher = Publisher()
        params = {
            "user_id": message.from_user.id,
            "task": "controlnet",
            "path_to_image_dir": path_to_image_dir,
            "img_name": img_name,
            "prompt_str": message.text,
        }
        publisher.send_message(params)
    
    else:
        msg = bot.send_message(message.from_user.id, 'Это не похоже на текст... Попробуй еще раз.')
        bot.register_next_step_handler(msg, get_controlnet_prompt)


bot.polling(none_stop=True, interval=0)
