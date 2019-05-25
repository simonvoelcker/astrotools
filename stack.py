import sys
import glob
import numpy as np

from functools import reduce
from PIL import Image
from util import load_image, save_image


def slice_image(image, x_offset, y_offset, x_size, y_size):
	return image[y_offset:y_offset+y_size,x_offset:x_offset+x_size]


def get_intersected_images(images, total_offset):
	height, width = images[0].shape
	x_offset, y_offset = total_offset
	intersection_width = width - x_offset
	intersection_height = height - y_offset
	print(f'intersection dimensions: {intersection_width}, {intersection_height}')

	for index, image in enumerate(images):
		# interpolate offset
		x_offset = int(float(total_offset[0])*float(index)/float(len(images)-1))
		y_offset = int(float(total_offset[1])*float(index)/float(len(images)-1))
		
		offset_image = slice_image(image, x_offset, y_offset, intersection_width, intersection_height)
		yield offset_image


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print(f'Usage: {sys.argv[0]} <filename_pattern> <total_offset(x,y)>')
		sys.exit(1)

	filename_pattern = sys.argv[1]
	files = glob.glob(filename_pattern)
	files.sort()
	# files = list(reversed(files))

	print(f'{len(files)} files')

	images = [
		load_image(filename)
		for filename in files
	]

	total_offset = sys.argv[2].split(',')
	total_offset = int(total_offset[0]), int(total_offset[1])

	stacked = reduce(np.add, get_intersected_images(images, total_offset))
	save_image(stacked, 'out.png')