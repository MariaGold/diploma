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
        pretrained_model = "/models/stable-diffusion-v1-5"
        prompt = "mksks"
        output_dir = f"/images_storage/LoRA/generated/{self.params['user_id']}" 
        instance_dir = f"/images_storage/LoRA/train/{self.params['user_id']}" 
        steps = 300
        batch_size = 1
        fp_16_arg = "fp16"
        lr = 3e-4
        lr_text_encoder = e-5
        new_lr = lr / batch_size
        new_lr_text_encoder = lr_text_encoder / batch_size

        command = (f'accelerate launch lora/training_scripts/train_lora_dreambooth.py '
             f'--pretrained_model_name_or_path="{pretrained_model}" '
             f'--instance_data_dir="{instance_dir}" '
             f'--output_dir="{output_dir}" '
             f'--instance_prompt="{prompt}" '
             f'--resolution=512 '
             f'--use_8bit_adam '
             f'--mixed_precision="{fp_16_arg}" '
             f'--train_batch_size=1 '
             f'--gradient_accumulation_steps=1 '
             f'--learning_rate={new_lr} '
             f'--lr_scheduler="constant" '
             f'--lr_warmup_steps=0 '
             f'--max_train_steps={steps} '
             f'--train_text_encoder '
             f'--lora_rank=16 '
             f'--learning_rate_text={new_lr_text_encoder}')
        os.system(command)




    def execute_lora_generate(self):
        pass