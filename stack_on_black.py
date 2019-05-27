import sys
import glob
import numpy as np

from functools import reduce
from PIL import Image
from util import load_image, save_image, create_image


def maximize_contrast(image):
	min_value = np.amin(image)
	max_value = np.amax(image)
	print(f'min: {min_value}, max: {max_value}, spread: {max_value - min_value}')
	if min_value == max_value:
		print('Not increasing constrast: It is zero.')		
		return image
	return (image - min_value) * (255.0 / (max_value - min_value))


def get_offset_padded_images(images, x_offset, y_offset):
	image_width, image_height = images[0].shape
	total_width = image_width + abs(x_offset)
	total_height = image_height + abs(y_offset)

	for index, image in enumerate(images):
		norm_index = float(index) / float(len(images)-1)
		# interpolate offset
		x = round(float(x_offset) * (1.0-norm_index))
		if x_offset < 0:
			x -= x_offset
		y = round(float(y_offset) * (1.0-norm_index))
		if y_offset < 0:
			y -= y_offset

		padded_image = create_image(total_width, total_height)
		padded_image[x:image_width+x, y:image_height+y] = image
		yield padded_image


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print(f'Usage: {sys.argv[0]} <filename_pattern> <total_offset(x,y)>')
		sys.exit(1)

	filename_pattern = sys.argv[1]
	files = glob.glob(filename_pattern)
	files.sort()

	print(f'{len(files)} files')

	images = [
		load_image(filename)
		for filename in files
	]

	x_offset, y_offset = sys.argv[2].split(',')
	x_offset = int(x_offset)
	y_offset = int(y_offset)

	stacked = reduce(np.add, get_offset_padded_images(images, x_offset, y_offset))
	stacked = maximize_contrast(stacked)
	save_image(stacked, 'out.png')
