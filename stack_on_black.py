import sys
import glob
import numpy as np

from functools import reduce
from PIL import Image
from util import load_image, save_image, create_image
from stack import interpolate_offsets


def maximize_contrast(image, max_channel_value=255.0):
	min_value = np.amin(image)
	max_value = np.amax(image)
	print(f'min: {min_value}, max: {max_value}, spread: {max_value - min_value}')
	if min_value == max_value:
		print('Not increasing constrast: It is zero.')		
		return image

	# do transform in float-space
	float_image = image.astype(float)
	stretched = (float_image - min_value) * (max_channel_value / (max_value - min_value))
	return stretched.astype(np.int16)


def stack_images_on_black(files, x_offset, y_offset, stride):

	image0 = load_image(files[0])
	image_width, image_height, channels = image0.shape

	total_width = image_width + abs(x_offset)
	total_height = image_height + abs(y_offset)

	image_offsets = interpolate_offsets(len(files), x_offset, y_offset)

	stacked_image = create_image(total_width, total_height, channels)
	for index, (x,y) in enumerate(image_offsets):		
		if index % stride != 0:
			continue
		image = load_image(files[index])
		padded_image = create_image(total_width, total_height, channels)
		padded_image[x:x+image_width, y:y+image_height, :] = image		
		stacked_image = np.add(stacked_image, padded_image)

	return stacked_image


if __name__ == '__main__':
	if len(sys.argv) not in (3,4):
		print(f'Usage: {sys.argv[0]} <filename_pattern> <total_offset(x,y)> <stride=1>')
		sys.exit(1)

	filename_pattern = sys.argv[1]
	files = glob.glob(filename_pattern)
	files.sort()

	if not files:
		print('No files')
		sys.exit(1)

	stride = int(sys.argv[3]) if len(sys.argv) == 4 else 1 
	print(f'{len(files)} files, stride={stride}')

	offsets = sys.argv[2].split(',')
	x_offset = int(offsets[0])
	y_offset = int(offsets[1])

	stacked_image = stack_images_on_black(files, x_offset, y_offset, stride)
	stacked_image = maximize_contrast(stacked_image, max_channel_value=255.0)
	save_image(stacked_image, 'stacked_on_black.png', rgb_mode=True)
