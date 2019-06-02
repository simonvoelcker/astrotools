import sys
import glob
import numpy as np

from functools import reduce
from PIL import Image
from util import load_image, save_image, create_image
from stack import interpolate_offsets


def maximize_contrast(image):
	min_value = np.amin(image)
	max_value = np.amax(image)
	print(f'min: {min_value}, max: {max_value}, spread: {max_value - min_value}')
	if min_value == max_value:
		print('Not increasing constrast: It is zero.')		
		return image
	return (image - min_value) * (255.0 / (max_value - min_value))


def stack_images_on_black(images, x_offset, y_offset):
	image_width, image_height, channels = images[0].shape
	total_width = image_width + abs(x_offset)
	total_height = image_height + abs(y_offset)

	image_offsets = interpolate_offsets(len(images), x_offset, y_offset)

	padded_images = []
	for image, (x,y) in zip(images, image_offsets):
		padded_image = create_image(total_width, total_height, channels)
		padded_image[x:x+image_width, y:y+image_height, :] = image
		padded_images.append(padded_image)

	stacked_image = reduce(np.add, padded_images)
	return stacked_image


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print(f'Usage: {sys.argv[0]} <filename_pattern> <total_offset(x,y)>')
		sys.exit(1)

	filename_pattern = sys.argv[1]
	files = glob.glob(filename_pattern)
	files.sort()

	files = files[:400]

	print(f'{len(files)} files')

	images = [
		load_image(filename)
		for filename in files
	]

	offsets = sys.argv[2].split(',')
	x_offset = int(offsets[0])
	y_offset = int(offsets[1])

	stacked_image = stack_images_on_black(images, x_offset, y_offset)
	stacked_image = maximize_contrast(stacked_image)
	save_image(stacked_image, 'stacked_on_black.png')
