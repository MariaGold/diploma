from Modules.ControlNet.ControlNet import ControlNet
from Modules.Prompt import Prompt

import telebot
import os

class Callback:
    def __init__(self, params):
        self.task = params['task']
        self.params = params
        self.bot = telebot.TeleBot(os.environ['TELEGRAM_API_TOKEN'])

    def execute(self):
        if self.task == 'controlnet':
            self.execute_controlnet()
        elif self.task == 'lora_learn':
            self.execute_lora_learn()
        elif self.task == 'lora_generate':
            self.execute_lora_generate()

    def execute_controlnet(self):
        prompt = Prompt(self.params['prompt_str'])
        model = ControlNet(self.params['path_to_image_dir'], self.params['img_name'], prompt)
        model.setup_model()
        result_path = model.generate()

        self.bot.send_message(self.params['user_id'], 'Готов?')

        result = open(result_path, 'rb')
        self.bot.send_photo(self.params['user_id'], result)

        text = 'Если результат не нравится, то большая вероятность, что дело в промпте.'
        text += ' Либо исходное изображение низкого качества. Но я сделал всё, что мог...'
        self.bot.send_message(self.params['user_id'], text)

    def execute_lora_learn(self):
        pass

    def execute_lora_generate(self):
        pass