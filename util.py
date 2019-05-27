import numpy as np

from PIL import Image


def load_image(filename):
	pil_image = Image.open(filename).convert('L') # to grayscale
	yx_image = np.asarray(pil_image, dtype=np.int16)
	return np.transpose(yx_image)


def save_image(image, filename):
	yx_image = np.transpose(image)
	yx_image = yx_image.astype(np.int8)
	pil_image = Image.fromarray(yx_image, mode='L')
	pil_image.save(filename)


def create_image(width, height):
	xy_image = Image.new(mode='I', size=(height, width))
	return np.asarray(xy_image, dtype=np.int16)
