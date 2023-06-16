from Modules.ControlNet.ControlNet import ControlNet
from Modules.Prompt import Prompt
from Modules.LoRA.LoRA import LoRA

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
        elif self.task == 'lora_train':
            self.execute_lora_train()
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

    def execute_lora_train(self):
        lora = LoRA(self.params['instance_dir'], self.params['output_dir'], None)
        lora.train()


    def execute_lora_generate(self):
        lora = LoRA(None, self.params['path_to_model'], self.params['prompt_str'])
        path_to_image = lora.generate()

        self.bot.send_message(self.params['user_id'], 'Готов?')

        result = open(path_to_image, 'rb')
        self.bot.send_photo(self.params['user_id'], result)

        text = 'Если результат не нравится, то большая вероятность, что дело в промпте.'
        text += ' Либо в обучающей выборке было мало хороших изображений. Но я сделал всё, что мог...'
        self.bot.send_message(self.params['user_id'], text)
