import sys
import glob
import numpy as np

from util import load_image, save_image, create_image


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


def stack_images_on_black(files, x_offset, y_offset, stride):

	image0 = load_image(files[0])
	image_width, image_height, channels = image0.shape

	total_width = image_width + abs(x_offset)
	total_height = image_height + abs(y_offset)

	image_offsets = interpolate_offsets(len(files), x_offset, y_offset)

	stacked_image = create_image(total_width, total_height, channels)
	samples = np.zeros((total_width, total_height))

	for index, (x,y) in enumerate(image_offsets):		
		if index % stride != 0:
			continue
		image = load_image(files[index])
		padded_image = create_image(total_width, total_height, channels)
		padded_image[x:x+image_width, y:y+image_height, :] = image		
		
		stacked_image = np.add(stacked_image, padded_image)

		samples[x:x+image_width, y:y+image_height] += 1

	return stacked_image, samples


def substract_pollution(image, samples):
	max_samples = np.amax(samples)
	min_pollution = None

	width, height, channels = image.shape
	for x in range(width):
		for y in range(height):
			if samples[x,y] == max_samples:
				for c in range(channels):
					pollution = image[x,y,c]
					if min_pollution is None or pollution < min_pollution:
						min_pollution = pollution 

	print(f'max samples={max_samples}, pollution={min_pollution}')

	pollution_image = samples.astype(float) / float(max_samples) * float(min_pollution) 
	
	result = np.zeros(image.shape, dtype=float)
	for channel in range(channels):
		result[:, :, channel] = image[:, :, channel] - pollution_image

	result = np.clip(result, 0.0, 1.0)
	return result


def normalize_image(image):
	min_value = np.amin(image)
	max_value = np.amax(image)
	if max_value == 0:
		print('Not normalizing image: It is all black.')		
		return image

	float_image = image.astype(float)
	normalized = (float_image - min_value) / (max_value - min_value)
	return normalized


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

	image, samples = stack_images_on_black(files, x_offset, y_offset, stride)

	#cx, cy, r = 2583, 934, 400
	#image = image[cx-r:cx+r, cy-r:cy+r, :]
	#samples = samples[cx-r:cx+r, cy-r:cy+r]

	print('stacked. unique values:', len(np.unique(image)))
	
	image = normalize_image(image)
	print('normalized. unique values:', len(np.unique(image)))
	
	image = substract_pollution(image, samples)
	print('depolluted. unique values:', len(np.unique(image)))
	
	image = normalize_image(image)
	print('normalized. unique values:', len(np.unique(image)))
	
	#image = np.square(image)
	#image = np.square(image)
	#image = np.sqrt(image)
	print('filtered. unique values:', len(np.unique(image)))
	
	image = (255.0 * image).astype(np.int16)
	print('converted to 16bit int. unique values:', len(np.unique(image)))

	# stacked_image = maximize_contrast(stacked_image, max_channel_value=255.0)
	
	save_image(image, 'stacked.png', rgb_mode=True)
