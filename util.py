import numpy as np

from PIL import Image


def load_image(filename):
	pil_image = Image.open(filename)
	#.convert('L') # to grayscale -> yx_image
	yxc_image = np.asarray(pil_image, dtype=np.int16)
	xyc_image = np.transpose(yxc_image, (1, 0, 2))
	return xyc_image


def save_image(image, filename, rgb_mode=True):
	if rgb_mode:
		yxc_image = np.transpose(image, (1, 0, 2))
		yxc_image = yxc_image.astype(np.int8)
		pil_image = Image.fromarray(yxc_image, mode='RGB')
	else:
		yxc_image = np.transpose(image, (1, 0, 2))
		yxc_image = yxc_image.astype(np.int32)
		# just pick R channel
		yx_image = yxc_image[:,:,0]
		pil_image = Image.fromarray(yx_image, mode='I')
	pil_image.save(filename)


def create_image(width, height, channels):
	xyc_image = Image.new(mode='RGB', size=(height, width))
	return np.asarray(xyc_image, dtype=np.int16)
