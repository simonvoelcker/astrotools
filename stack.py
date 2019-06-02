import sys
import glob
import numpy as np

from functools import reduce
from PIL import Image
from util import load_image, save_image


def maximize_contrast(image):
	min_value = np.amin(image)
	max_value = np.amax(image)
	print(f'min: {min_value}, max: {max_value}, spread: {max_value - min_value}')
	if min_value == max_value:
		print('Not increasing constrast: It is zero.')		
		return image
	return (image - min_value) * (255.0 / (max_value - min_value))


def interpolate_offsets(num_images, x_offset, y_offset):
	for index in range(num_images):
		norm_index = float(index) / float(num_images-1)
		# interpolate offset
		x = round(float(x_offset) * (1.0-norm_index))
		if x_offset < 0:
			x -= x_offset
		y = round(float(y_offset) * (1.0-norm_index))
		if y_offset < 0:
			y -= y_offset
		yield x, y


def stack_images(images, x_offset, y_offset):
	
	# images are shifted against the offset direction
	x_offset = -x_offset
	y_offset = -y_offset

	width, height, channels = images[0].shape
	intersection_width = width - abs(x_offset)
	intersection_height = height - abs(y_offset)
	print(f'intersection dimensions: {intersection_width}, {intersection_height}')

	image_offsets = interpolate_offsets(len(images), x_offset, y_offset)

	sliced_images = [
		image[x:x+intersection_width, y:y+intersection_height]
		for image, (x, y) in zip(images, image_offsets)
	]

	stacked_image = reduce(np.add, sliced_images)
	return stacked_image


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print(f'Usage: {sys.argv[0]} <filename_pattern> <total_offset(x,y)>')
		sys.exit(1)

	filename_pattern = sys.argv[1]
	files = glob.glob(filename_pattern)
	files.sort()

	files = files[:200]

	print(f'{len(files)} files')

	images = [
		load_image(filename)
		for filename in files
	]

	offsets = sys.argv[2].split(',')
	x_offset = int(offsets[0])
	y_offset = int(offsets[1])

	stacked_image = stack_images(images, x_offset, y_offset)
	stacked_image = maximize_contrast(stacked_image)
	save_image(stacked_image, 'stacked.png')
