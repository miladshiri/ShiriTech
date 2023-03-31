import openai
import deepai
import requests
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageSequenceClip
from io import BytesIO
from numpy import asarray
import json

openai.api_key = ""
deepai_api_key = ""
apitemplate_api_key = ""
template_id = ""

def get_random_topic_facts(num_facts=10):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= [{"role": "user", "content": f"Give me {num_facts} facts about a random interesting topic. You choose the topic."}],
        temperature=0.7,
    )
    facts = response.choices[0].message.content.strip().split('\n')
    return facts[:num_facts]   

def deepai_api(text):
    r = requests.post(
        "https://api.deepai.org/api/text2img",
        data={
            'text': text,
        },
        headers={'api-key': deepai_api_key}
    )
    return r.json()

def generate_image(prompt):
    response = deepai_api(prompt)
    print(response)
    image_url = response['output_url']
    image_data = requests.get(image_url).content
    image = Image.open(BytesIO(image_data))
    return image, image_url

def add_fact_overlay(image, fact):
    width, height = image.size
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 24)
    text_width, text_height = draw.textsize(fact, font)
    
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    
    draw.text((x, y), fact, font=font, fill=(255, 255, 255))

def create_video(images, fps=1):
    clip = ImageSequenceClip(images, fps=fps)
    clip.write_videofile("facts_video.mp4", codec="libx264", fps=fps)



def text_on_image(text, image):
    data = {
    "overrides": [
        {
            "name": "background-color",
            "stroke": "grey",
            "backgroundColor": "#393939"
        },
        {
            "name": "rect_1",
            "stroke": "#FFFFFF",
            "backgroundColor": "#626262"
        },
        {
            "name": "background-image",
            "stroke": "grey",
            "src": image
        },
        {
            "name": "text_quote",
            "text": text,
            "textBackgroundColor": "#545454",
            "color": "#F6F6F6"
        }
    ]
    }

    response = requests.post(
        F"https://rest.apitemplate.io/v2/create-image?template_id={template_id}",
        headers = {"X-API-KEY": F"{apitemplate_api_key}"},
        json= data
    )
    res = response.json()
    image_data = requests.get(res['download_url']).content
    image = asarray(Image.open(BytesIO(image_data)))
    return image




if __name__ == "__main__":
    facts = get_random_topic_facts(5)
    print(facts)
    
    
    images = []
    for fact in facts:
        if not len(fact) > 5:
            continue
        image, image_url = generate_image(fact)
        # add_fact_overlay(image, fact)
        image = text_on_image(fact, image_url)
        images.append(image)
    
    new_images = []
    for image in images:
        new_images.append(asarray(image))
    create_video(new_images)
