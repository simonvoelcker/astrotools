import sys
import numpy as np

from PIL import Image
from util import load_image, save_image


def maximize_contrast(image):
	pass


if __name__ == '__main__':
	if len(sys.argv) != 2:
		print(f'Usage: {sys.argv[0]} <filename>')
		sys.exit(1)

	filename = sys.argv[1]
	image = load_image(filename)

	image = maximize_contrast(image)
	save_image(image, 'out.png')