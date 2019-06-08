import numpy as np

from util import load_image, save_image


class StackedImage:

	def __init__(self, files, x_offset, y_offset, stride):

		image0 = load_image(files[0])
		image_width, image_height, channels = image0.shape

		total_width = image_width + abs(x_offset)
		total_height = image_height + abs(y_offset)

		image_offsets = self.interpolate_offsets(len(files), x_offset, y_offset)

		stacked_image = np.zeros((total_width, total_height, channels), dtype=np.int16)
		samples = np.zeros((total_width, total_height))

		for index, (x,y) in enumerate(image_offsets):		
			if index % stride != 0:
				continue
			image = load_image(files[index])
			padded_image = np.zeros((total_width, total_height, channels), dtype=np.int16)
			padded_image[x:x+image_width, y:y+image_height, :] = image		
			
			stacked_image = np.add(stacked_image, padded_image)

			samples[x:x+image_width, y:y+image_height] += 1

		self.image = stacked_image
		self.samples =samples

	@staticmethod
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

	def normalize(self):
		min_value = np.amin(self.image)
		max_value = np.amax(self.image)
		if max_value == 0:
			print('Not normalizing image: It is all black.')		
			return

		float_image = self.image.astype(float)
		normalized = (float_image - min_value) / (max_value - min_value)
		self.image = normalized

	def substract_pollution(self):
		max_samples = np.amax(self.samples)
		min_pollution = None

		width, height, channels = self.image.shape
		for x in range(width):
			for y in range(height):
				if self.samples[x,y] == max_samples:
					for c in range(channels):
						pollution = self.image[x,y,c]
						if min_pollution is None or pollution < min_pollution:
							min_pollution = pollution 

		print(f'max samples per pixel: {max_samples}, pollution: {min_pollution:.4}')

		pollution_image = self.samples.astype(float) / float(max_samples) * float(min_pollution) 
		
		result = np.zeros(self.image.shape, dtype=float)
		for channel in range(channels):
			result[:, :, channel] = self.image[:, :, channel] - pollution_image

		result = np.clip(result, 0.0, 1.0)
		self.image = result

	def crop(self, cx, cy, r):
		# crop image to a square with center <cx,cy> and radius <>.
		self.image = self.image[cx-r:cx+r, cy-r:cy+r, :]
		self.samples = self.samples[cx-r:cx+r, cy-r:cy+r]

	def apply_gamma(self, gamma):
		self.image = np.power(self.image, gamma)

	def invert(self):
		self.image = 1.0 - self.image

	def save(self, filename):
		image_int = (255.0 * self.image).astype(np.int16)
		save_image(image_int, filename)
