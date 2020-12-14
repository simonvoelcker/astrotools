import numpy as np

from PIL import ImageFilter


def pick_guiding_region(frame, radius):
    image = frame.get_pil_image()
    image = image.crop((
        radius,
        radius,
        image.width - radius,
        image.height - radius,
    ))
    image = image.filter(filter=ImageFilter.GaussianBlur(5))
    np_image = np.asarray(image)
    np_image = np.mean(np_image, axis=2)
    np_image = np.flip(np_image, axis=0)

    max_point = np.unravel_index(np.argmax(np_image), np_image.shape)

    # square region of given radius around the brightest pixel
    # because of cropping earlier, this is offset by 1*region_radius
    return {
        'x': max_point[1].item(),
        'y': max_point[0].item(),
        'width': 2 * radius,
        'height': 2 * radius,
    }
