import sys
import glob
import numpy as np

from PIL import Image
from util import load_image


def get_similarity(image1, image2):
	assert image1.shape == image2.shape

	abs_difference = 0
	for y in range(image1.shape[0]):
		for x in range(image1.shape[1]):
			abs_difference += abs(image1[y,x] - image2[y,x])

	rel_difference = float(abs_difference) / (image1.shape[0]*image1.shape[1]*255.0)
	return 1.0 - rel_difference


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print(f'Usage: {sys.argv[0]} <filename1> <filename2>')
		sys.exit(1)

	filename1, filename2 = sys.argv[1], sys.argv[2]
	image1 = load_image(filename1)
	image2 = load_image(filename2)

	similarity = get_similarity(image1, image2)

	print(similarity)