from StringIO import StringIO

import requests
import syncano
from PIL import Image


def connect_syncano():
    return syncano.connect(instance_name=META['instance'],
                           api_key=CONFIG['syncano_api_key'])


def convert_to_sepia(image):
    # source: http://effbot.org/zone/pil-sepia.htm

    def make_linear_ramp(white):
        # putpalette expects [r,g,b,r,g,b,...]

        r, g, b = white
        ramp = []
        for i in range(255):
            ramp.extend((r * i / 255, g * i / 255, b * i / 255))
        return ramp

    # make sepia ramp (tweak color as necessary)
    sepia = make_linear_ramp((255, 240, 192))

    # convert to grayscale
    image = image.convert("L")

    # apply sepia palette
    image.putpalette(sepia)

    return image.convert("RGB")


def get_image(image_url):
    if image_url is None:
        raise 'Image URL not provided.'

    r = requests.get(image_url)

    return Image.open(StringIO(r.content))


def process_image(image, processing_function):
    return processing_function(image)


def save_image(image, title):
    tmp_img_path = '/tmp/tmp_img.jpg'
    image.save(tmp_img_path)

    registry = connect_syncano()
    with open(tmp_img_path, 'rb') as img:
        image_obj = registry.objects.create(
            class_name='image',
            instance_name=registry.instance_name,
            title=title,
            image=img
        )
    # after save() URL represents file
    return image_obj.image


def run():
    image = get_image(ARGS['image_url'])
    processed_img = process_image(image, convert_to_sepia)
    return save_image(processed_img, ARGS['title'])


print(run())
