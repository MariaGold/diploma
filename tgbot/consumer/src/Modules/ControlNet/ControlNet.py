from PIL import Image
import numpy as np
import torch
import cv2
import os

from diffusers.utils import load_image
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from diffusers import UniPCMultistepScheduler
from transformers import pipeline

from Modules.Prompt import Prompt


class ControlNet():
    def __init__(self, path_to_image_dir: str, img_name: str, prompt: Prompt):
        self.path_to_image_dir = path_to_image_dir
        self.image_name = img_name
        self.path_to_image = os.path.join(path_to_image_dir, img_name)
        self.prompt = prompt
        self.image_class = prompt.image_class

    def get_canny(self):
        image = load_image(self.path_to_image)
        image = np.array(image)

        low_threshold = 100
        high_threshold = 200

        image = cv2.Canny(image, low_threshold, high_threshold)
        image = image[:, :, None]
        image = np.concatenate([image, image, image], axis=2)
        canny_image = Image.fromarray(image)

        return canny_image
    
    def get_depth(self):
        image = load_image(self.path_to_image)

        depth_estimator = pipeline('depth-estimation')

        image = load_image(self.path_to_image)
        image = depth_estimator(image)['depth']
        image = np.array(image)
        image = image[:, :, None]
        image = np.concatenate([image, image, image], axis=2)
        depth_image = Image.fromarray(image)

        return depth_image
    
    def setup_model(self):
        canny_image = self.get_canny()
        self.image = canny_image

        controlnet = ControlNetModel.from_pretrained("/models/sd-controlnet-canny", torch_dtype=torch.float16)
        
        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "/models/stable-diffusion-v1-5", controlnet=controlnet, torch_dtype=torch.float16
        )

        self.pipe.scheduler = UniPCMultistepScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.enable_model_cpu_offload()
        #self.pipe.enable_xformers_memory_efficient_attention()

    def setup_multi_model(self):
        canny_image = self.get_canny()
        depth_image = self.get_depth()
        self.image = [canny_image, depth_image]

        canny_controlnet = ControlNetModel.from_pretrained("/models/sd-controlnet-canny", torch_dtype=torch.float16)
        depth_controlnet = ControlNetModel.from_pretrained("/models/sd-controlnet-depth", torch_dtype=torch.float16)
        controlnet = [canny_controlnet, depth_controlnet]

        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "/models/stable-diffusion-v1-5", controlnet=controlnet, torch_dtype=torch.float16
        )

        self.pipe.scheduler = UniPCMultistepScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.enable_model_cpu_offload()
        #self.pipe.enable_xformers_memory_efficient_attention()

    def generate(self):
        generator = torch.Generator(device="cpu").manual_seed(2)

        output = self.pipe(
            self.prompt.positive,
            self.image, 
            negative_prompt=self.prompt.negative,
            num_inference_steps=25,
            generator=generator
        )

        result = output.images[0]
        path = os.path.join(self.path_to_image_dir, f'result_{self.image_name}')
        result.save(path)

        return path
