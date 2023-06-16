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
    text += '\n/lora_gen_{model_id} - сгенерировать изображение на основе модели по ее идентификатору'
    text += '\n/stats - статистика использования сервиса'
    text += '\n/stop - с помощью этой команды можно прервать диалог с мной'

    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['controlnet'])
def controlnet(message):
    text = '''
    Пришли мне изображение хорошего качества.
    '''
    msg = bot.send_message(message.from_user.id, text)
    bot.register_next_step_handler(msg, get_controlnet_photo)


def get_controlnet_photo(message):
    if message.content_type == 'photo':
        raw = message.photo[-1].file_id
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
    elif message.content_type == 'text':
        if message.text == '/stop':
            text = 'Хорошо, давай сначала... :)'
            msg = bot.send_message(message.from_user.id, text)
        else:
            text = 'Не понял тебя, давай еще раз попробуем. Пришли мне фотографию.'
            msg = bot.send_message(message.from_user.id, text)
            bot.register_next_step_handler(msg, get_controlnet_photo)
    else:
        text = 'Эй, ну ты чего, это же не фотка. Загрузи именно изображение плз и не в виде файла :)'
        msg = bot.send_message(message.from_user.id, text)
        bot.register_next_step_handler(msg, get_controlnet_photo)


def get_controlnet_prompt(message, path_to_image_dir, img_name):
    if message.content_type == 'text':
        if message.text == '/stop':
            text = 'Хорошо, давай сначала... :)'
            msg = bot.send_message(message.from_user.id, text)
        else:
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


@bot.message_handler(commands=['lora_train'])
def lora_train(message):
    text = '''
    Пришли мне одно изображение в хорошем качестве (не файлом!).
    '''
    msg = bot.send_message(message.from_user.id, text)
    bot.register_next_step_handler(msg, get_lora_photos, None, None)


def get_lora_photos(message, path_to_images_dir, model_id):
    if message.content_type == 'photo':
        raw = message.photo[-1].file_id
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)

        images_num = 0
        if path_to_images_dir is None:
            path_to_images_dir = os.path.join('/', 'images_storage', 'LoRA', 'train', str(message.from_user.id))
            if not os.path.exists(path_to_images_dir):
                os.mkdir(path_to_images_dir)
            
            model_id = str(int(datetime.now().timestamp()))
            path_to_images_dir = os.path.join(path_to_images_dir, model_id)
            os.mkdir(path_to_images_dir)
        else:
            images_num = len(os.listdir(path_to_images_dir))

        img_name = str(images_num + 1) + ".jpg"
        path_to_image = os.path.join(path_to_images_dir, img_name)

        with open(path_to_image,'wb') as new_file:
            new_file.write(downloaded_file)

        text = 'Супер, фото я загрузил. Если хочешь добавить еще, то присылай по одной штуке в сообщении.'
        text += ' Если всё, то нажимай кнопку "Обучить!"'
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        btns = []
        btns.append(types.KeyboardButton('Обучить!'))
        markup.add(*btns)

        msg = bot.send_message(message.from_user.id, text, reply_markup = markup)
        bot.register_next_step_handler(msg, get_lora_photos, path_to_images_dir, model_id)
    elif message.content_type == 'text':
        if message.text == 'Обучить!':
            bot.send_message(message.from_user.id, 
                         'Всё хорошо. Ставлю обучение в очередь...', 
                         reply_markup = types.ReplyKeyboardRemove())

            publisher = Publisher()
            params = {
                "user_id": message.from_user.id,
                "task": "lora_train",
                "instance_dir": path_to_images_dir,
                "output_dir": path_to_images_dir.replace('train', 'generated'),
                "model_id": model_id,
            }
            publisher.send_message(params)
        elif message.text == '/stop':
            text = 'Хорошо, давай сначала... :)'
            msg = bot.send_message(message.from_user.id, text)
        else:
            bot.send_message(message.from_user.id, 
                         'Что-то странное ты присылаешь, конечно... Попробуй еще раз', 
                         reply_markup = types.ReplyKeyboardRemove())
    else:
        text = 'Эй, ну ты чего, это же не фотка. Загрузи именно изображение плз и не в виде файла :)'
        msg = bot.send_message(message.from_user.id, text)
        bot.register_next_step_handler(msg, get_lora_photos)


def check_lora_model_dir(path_to_model):
    loras = ['lora_weight.pt', 'lora_weight.safetensors', 'lora_weight.text_encoder.pt']
    ok = True
    for lora in loras:
        if not os.path.exists(os.path.join(path_to_model, lora)):
            ok = False
    return ok


@bot.message_handler(commands=['lora_list'])
def lora_list(message):
    models_dir = os.path.join('/', 'images_storage', 'LoRA', 'generated', str(message.from_user.id))

    text = ''

    if not os.path.exists(models_dir):
        text = 'Для тебя еще не обучена ни одна модель. Если хочешь начать обучение, жми /lora_train'
    else:
        models = os.listdir(models_dir)
        models.sort(reverse=True)
        num = 0
        text = 'Доступные модели:\n'
        for model_id in models:
            path_to_model = os.path.join(models_dir, model_id, 'model')
            if check_lora_model_dir(path_to_model):
                dt = datetime.fromtimestamp(int(model_id))
                text += f'\nМодель от {dt} - /lora_gen_{model_id}'
                num += 1
            if num >= 5: break

        if num == 0:
            text = 'Для тебя еще не обучена ни одна модель. Если хочешь начать обучение, жми /lora_train'

    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['lora_gen'])
def lora_gen(message):
    models_dir = os.path.join('/', 'images_storage', 'LoRA', 'generated', str(message.from_user.id))

    text = ''

    if not os.path.exists(models_dir):
        text = 'Для тебя еще не обучена ни одна модель. Если хочешь начать обучение, жми /lora_train'
        bot.send_message(message.from_user.id, text)
    else:
        models = os.listdir(models_dir)
        if len(models) > 0:
            models.sort(reverse=True)
            model_id = models[0]

            path_to_model = os.path.join(models_dir, model_id, 'model')
            if check_lora_model_dir(path_to_model):
                text = 'Что ж, модель я нашел. Теперь пришли, пожалуйста, промпт для генерации.'
                msg = bot.send_message(message.from_user.id, text)
                bot.register_next_step_handler(msg, get_lora_prompt, path_to_model)
            else:
                text = 'Для тебя еще не обучена ни одна модель. Если хочешь начать обучение, жми /lora_train'
                bot.send_message(message.from_user.id, text)
        else:
            text = 'Для тебя еще не обучена ни одна модель. Если хочешь начать обучение, жми /lora_train'
            bot.send_message(message.from_user.id, text)


def get_lora_prompt(message, path_to_model):
    if message.content_type == 'text':
        if message.text == '/stop':
            text = 'Хорошо, давай сначала... :)'
            msg = bot.send_message(message.from_user.id, text)
        else:
            bot.send_message(message.from_user.id, 
                            'Всё хорошо. Ставлю генерацию в очередь...')

            publisher = Publisher()
            params = {
                "user_id": message.from_user.id,
                "task": "lora_generate",
                "path_to_model": path_to_model,
                "prompt_str": message.text,
            }
            publisher.send_message(params)
    
    else:
        msg = bot.send_message(message.from_user.id, 'Это не похоже на текст... Попробуй еще раз.')
        bot.register_next_step_handler(msg, get_lora_prompt)


@bot.message_handler(content_types=['text'])
def handle_other_messages(message):
    if str.find(message.text, '/lora_gen') == 0:
        model_id = message.text.replace('/lora_gen_', '')
        path_to_model = os.path.join('/', 'images_storage', 'LoRA', 'generated', str(message.from_user.id), model_id, 'model')

        if not check_lora_model_dir(path_to_model):
            bot.send_message(message.from_user.id, 'Такой модели не существует, мне очень жаль... Попробуем еще раз?')
        else:
            text = 'Что ж, модель такую я нашел. Теперь пришли, пожалуйста, промпт для генерации.'
            msg = bot.send_message(message.from_user.id, text)
            bot.register_next_step_handler(msg, get_lora_prompt, path_to_model)
    else:
        msg = bot.send_message(message.from_user.id, 'Моя твою не понимать.')


bot.polling(none_stop=True, interval=0)
