import sys
import glob
import numpy as np

from PIL import Image
from util import load_image
from similarity import get_similarity


def get_slice_1(size, offset):
	if offset >= 0:
		return offset, size
	else:
		return 0, size + offset


def get_slice_2(size, offset):
	return get_slice_1(size, -offset)


def slice_image(image, x_offset, y_offset, slice_f):
	min_x, max_x = slice_f(image.shape[1], x_offset)
	min_y, max_y = slice_f(image.shape[0], y_offset)
	return image[min_y:max_y,min_x:max_x]


def best_offset_in_area(image1, image2, base_offset, radius):
	best_offset = 0, 0
	best_similarity = 0
	for x_ofs in range(-radius+base_offset[0], radius+base_offset[0]+1, radius):
		for y_ofs in range(-radius+base_offset[1], radius+base_offset[1]+1, radius):
			similarity = get_similarity(
				slice_image(image1, x_ofs, y_ofs, get_slice_1),
				slice_image(image2, x_ofs, y_ofs, get_slice_2),
			)
			if similarity > best_similarity:
				print(f'new best: {x_ofs}, {y_ofs}')
				best_similarity = similarity
				best_offset = x_ofs, y_ofs

	return best_offset


def get_offset(image1, image2):
	assert image1.shape == image2.shape

	radius = 16
	offset = 0, 0

	while radius >= 1:
		offset = best_offset_in_area(image1, image2, offset, radius)
		radius = int(radius/2)

	return offset


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print(f'Usage: {sys.argv[0]} <filename1> <filename2>')
		sys.exit(1)

	filename1, filename2 = sys.argv[1], sys.argv[2]
	image1 = load_image(filename1)
	image2 = load_image(filename2)

	offset = get_offset(image1, image2)
	print(f'offset: {offset}')