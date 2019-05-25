import numpy as np

from PIL import Image


def load_image(filename):
	image = Image.open(filename).convert('L') # to grayscale
	return np.asarray(image, dtype=np.int8)


def save_image(array, filename):
	image = Image.fromarray(array, mode='L')
	image.save(filename)
