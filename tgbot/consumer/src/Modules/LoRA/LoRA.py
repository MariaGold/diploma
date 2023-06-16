import torch
from lora_diffusion import monkeypatch_or_replace_lora, tune_lora_scale
from diffusers import StableDiffusionPipeline
from datetime import datetime
import os

from Modules.Prompt import Prompt


class LoRA():
    def __init__(self, instance_dir, output_dir, prompt=None):
        self.path_to_train = instance_dir
        self.path_to_model = output_dir
        self.prompt = prompt

    
    def train(self):
        pretrained_model = "/models/stable-diffusion-v1-5"
        prompt = "mksks"
        
        instance_dir = self.path_to_train
        output_dir = self.path_to_model
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
            output_dir = os.path.join(output_dir, 'model')
            os.mkdir(output_dir)

        if not os.path.exists(output_dir.replace('model', 'images')):
            os.mkdir(output_dir.replace('model', 'images'))

        steps = 300
        batch_size = 1
        fp_16_arg = "fp16"
        lr = 3e-4
        lr_text_encoder = 1e-5
        new_lr = lr / batch_size
        new_lr_text_encoder = lr_text_encoder / batch_size

        command = (f'accelerate launch /app/Modules/LoRA/utils/training_scripts/train_lora_dreambooth.py '
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

    def generate(self):
        pipe = StableDiffusionPipeline.from_pretrained("/models/stable-diffusion-v1-5", 
                                                       torch_dtype=torch.float16).to("cuda")
        monkeypatch_or_replace_lora(pipe.unet, 
                                    torch.load(os.path.join(self.path_to_model, "lora_weight.pt")))
        monkeypatch_or_replace_lora(pipe.text_encoder, 
                                    torch.load(os.path.join(self.path_to_model, "lora_weight.text_encoder.pt")), 
                                    target_replace_module=["CLIPAttention"])
        
        prompt = Prompt(self.prompt).positive
        lora_scale_unet = 0.1
        lora_scale_text_encoder = 0.1
        guidance = 1.4

        tune_lora_scale(pipe.unet, lora_scale_unet)
        tune_lora_scale(pipe.text_encoder, lora_scale_text_encoder)

        image = pipe(prompt, num_inference_steps=50, guidance_scale=guidance).images[0]

        image_name = str(int(datetime.now().timestamp())) + '.png'
        path_to_save = os.path.join(self.path_to_model.replace('model', 'images'), image_name)

        image.save(path_to_save)

        return path_to_save
