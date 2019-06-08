import numpy as np

from PIL import Image


def load_image(filename, dtype):
	pil_image = Image.open(filename)
	yxc_image = np.asarray(pil_image, dtype=dtype)
	xyc_image = np.transpose(yxc_image, (1, 0, 2))
	return xyc_image


def save_image(image, filename):
	yxc_image = np.transpose(image, (1, 0, 2))
	yxc_image = yxc_image.astype(np.int8)
	pil_image = Image.fromarray(yxc_image, mode='RGB')
	pil_image.save(filename)
