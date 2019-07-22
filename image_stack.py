import os
import sys
import numpy as np

from PIL import Image


class ImageStack:

	def __init__(self, frames, dtype=np.int16):

		# frames = list(self._prestacked_frames(frames, agg_count=33))

		print(f'Stacking image from {len(frames)} frames')

		width, height, channels = frames[0].shape

		image_stack = np.zeros((width, height, channels, len(frames)), dtype=dtype)
		for index, frame in enumerate(frames):
			image_stack[:, :, :, index] = frame

		self.image = np.median(image_stack, axis=3)
		self.samples = np.ones((width, height), dtype=np.int16)

		if np.amin(self.image) < 0:
			print('An overflow occurred during stacking. Consider using --bits=32')
			sys.exit(1)

	@staticmethod
	def _prestacked_frames(frames, agg_count):
		for index, frame in enumerate(frames):
			if index % agg_count == 0:
				agg_frame = np.zeros(frames[0].shape, dtype=np.int16)
			agg_frame += frame
			if (index+1) % agg_count == 0:
				yield agg_frame


	@staticmethod
	def _get_sharpness(xyc_image):
		xy_image = np.sum(xyc_image, axis=2)
		gy, gx = np.gradient(xy_image)
		gnorm = np.sqrt(gx**2 + gy**2)
		return np.average(gnorm)

	def normalize(self):
		min_value = np.amin(self.image)
		max_value = np.amax(self.image)
		if max_value == 0:
			print('Not normalizing image: It is all black.')		
			return

		float_image = self.image.astype(float)
		if max_value > min_value:
			normalized = (float_image - min_value) / (max_value - min_value)
		else:
			normalized = (float_image - min_value)

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

		print(f'max samples per pixel: {max_samples}, pollution: {float(min_pollution):.4}')

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
		out_image = (255.0 * self.image)
		yxc_image = np.transpose(out_image, (1, 0, 2))
		yxc_image = yxc_image.astype(np.int8)
		pil_image = Image.fromarray(yxc_image, mode='RGB')
		pil_image.save(filename)
