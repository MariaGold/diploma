import os

class Prompt():
    def __init__(self, prompt_body, image_class = None):
        self.body = prompt_body
        self.image_class = image_class

        self.create_prompt()

    def create_prompt(self):
        self.positive = ''
        self.negative = ''

        if self.body == 'Fantasy':
            self.body = 'fantasy style'
        elif self.body == 'Realistic':
            self.body = 'Super realistic photo'
        elif self.body == 'The Witcher':
            self.body = 'The Wicher style'
        elif self.body == 'Cyberpank':
            self.body = 'cyberpank style'

        self.positive += self.body
        self.positive += ', extremely detailed, high quality'
        self.negative += "monochrome, lowres, bad anatomy, worst quality, low quality"
