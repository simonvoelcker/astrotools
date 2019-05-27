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


def get_offset_padded_images(images, total_offset):
	image_height, image_width = images[0].shape
	x_offset, y_offset = total_offset
	total_width = image_width + abs(x_offset)
	total_height = image_height + abs(y_offset)

	for index, image in enumerate(images):
		norm_index = float(index) / float(len(images)-1)
		# interpolate offset
		x_offset = round(float(total_offset[0]) * (1.0-norm_index))
		if total_offset[0] < 0:
			x_offset -= total_offset[0]
		y_offset = round(float(total_offset[1]) * (1.0-norm_index))
		if total_offset[1] < 0:
			y_offset -= total_offset[1]

		padded_image = create_image(total_width, total_height)
		padded_image[y_offset:image_height+y_offset, x_offset:image_width+x_offset] = image
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

	total_offset = sys.argv[2].split(',')
	total_offset = int(total_offset[0]), int(total_offset[1])

	stacked = reduce(np.add, get_offset_padded_images(images, total_offset))
	stacked = maximize_contrast(stacked)
	save_image(stacked, 'out.png')
