import numpy as np

from PIL import Image


def load_image(filename):
	image = Image.open(filename).convert('L') # to grayscale
	return np.asarray(image, dtype=np.int16)


def save_image(array, filename):
	array = array.astype(np.int8)
	image = Image.fromarray(array, mode='L')
	image.save(filename)


def create_image(width, height):
	image = Image.new(mode='I', size=(width, height))
	return np.asarray(image, dtype=np.int16)
