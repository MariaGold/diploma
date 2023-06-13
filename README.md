# Master's Thesis

## ![Abstract](https://downloader.disk.yandex.ru/preview/5ed7d9919dcb2af908dbc4283aba20ce86262bf3a73f4286fc26a0b75e0eb177/64891c40/McP72MjPXbUEsspx3DimPtq4gDq7QMmwej4No8eiekxL7x36c3PY1nLQvodAvpyoNxHyHhtALCOGpkAZF9gQZQ%3D%3D?uid=0&filename=1.png&disposition=inline&hash=&limit=0&content_type=image%2Fpng&owner_uid=0&tknv=v2&size=2048x2048)
## Abstract
<table>
<tr>
<td>
  This diploma thesis is devoted to the development of a telegram-bot for images style transfer and generating. The main goal of the work is to create an effective and user-friendly application that will allow users to easily and quickly transfer the style of images based on provided style description as well as generating new images of the desired object. The review of existing style transfer methods were carried out, including methods based on optimization, deep neural networks, generative adversarial networks, autoencoders and state-of-the-art Stable Diffusion methods with its extensions. The result of the work is a telegram-bot that allows training the neural network with LoRA or ControlNet to generate images of a particular object in the style described by a short prompt. Further research in this field may include improving the quality of style transfer results, speeding up the training and inference time, expanding the functionality of the application, and adapting style transfer methods to other types of data, such as audio and video.

</td>
</tr>
</table>


## Masters's thesis text

[Diploma](https://docs.google.com/document/d/1CSeM0fYHYugK_CLm7hD8S6BV0ALlk122fC7sCN3rgHA/edit?usp=sharing)

## Architecture

The application consists of several services wrapped into docker-containers. 
- Producer (manages messages from users and sends tasks in a queue to Consumer using AMQP protocol)
- Consumer (gets tasks from Producer using AMQP protocol)
- Postgres (local database storing users' information)
- RabbitMQ (works as a tasks manager in a queue)

As far as the application was developped aimimg at running it locally on a machine of medium power, the queue approach is used. This allows to organize tasks operation. RabbitMQ is responsible for tasks management.

As an image storage I use the local machine itself. At the same time, PosgresQL database is used for storing users' information. The database is organized locally as well and runs in a docker-container.

Producer and Consumer share some volume between each other in order to get an access to the images storage.

## Running the telegram bot
Before running the bot you must substitute your bot credentials in docker-compose file as well as download models for Stable Diffusion and ControlNet. Then you can run thee following command in terminal
<table>
<tr>
<td>
docker-compose up --build
</td>
</tr>
</table>
