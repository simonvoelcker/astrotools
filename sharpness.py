import sys
import glob
import numpy as np

from PIL import Image
from util import load_image


def get_sharpness(array):
	gy, gx = np.gradient(array)
	gnorm = np.sqrt(gx**2 + gy**2)
	return np.average(gnorm)


def get_sharpness_array(image_array, block_size=120):
	height, width = image_array.shape
	blk_x = int(width/block_size)
	blk_y = int(height/block_size)

	sharpness_array = np.zeros([blk_y, blk_x])

	for y in range(blk_y):
		for x in range(blk_x):
			slice = image_array[y*block_size:(y+1)*block_size,x*block_size:(x+1)*block_size]
			sharpness = get_sharpness(slice)
			sharpness_array[y,x] = sharpness
	
	return sharpness_array

def sharpness_array_to_grayscale(sharpness_array):
	max_sharpness = np.max(sharpness_array)
	normalize_factor = 255.0 / max_sharpness
	sharpness_array = sharpness_array * normalize_factor
	return sharpness_array.astype(int)


if __name__ == '__main__':
	if len(sys.argv) != 2:
		print(f'Usage: {sys.argv[0]} <filename_pattern>')
		sys.exit(1)

	filename_pattern = sys.argv[1]
	files = glob.glob(filename_pattern)

	images = [
		load_image(file)
		for file in files
	]
	sharpness_arrays = [
		get_sharpness_array(image)
		for image in images
	]
	shape = sharpness_arrays[0].shape
	best_sharpness = np.zeros(shape)

	for y in range(shape[0]):
		for x in range(shape[1]):
			sharpnesses = [
				sharpness_array[y,x]
				for sharpness_array in sharpness_arrays
			]
			best = max(sharpnesses)
			best_sharpness[y,x] = sharpnesses.index(best)

	print(best_sharpness)