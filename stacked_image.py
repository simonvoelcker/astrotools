import sys
import numpy as np

from PIL import Image


class StackedImage:

	def __init__(self, files, x_offset, y_offset, stride, bits, crop_input):

		dtype = np.int16 if bits == 16 else np.int32

		frame_0 = self._load_frame(files[0], dtype, crop_input)
		image_width, image_height, channels = frame_0.shape

		total_width = image_width + abs(x_offset)
		total_height = image_height + abs(y_offset)

		image_offsets = self._interpolate_offsets(len(files), x_offset, y_offset)

		self.image = np.zeros((total_width, total_height, channels), dtype=dtype)
		self.samples = np.zeros((total_width, total_height))

		for index, (x,y) in enumerate(image_offsets):
			if index % stride != 0:
				continue
			frame = self._load_frame(files[index], dtype, crop_input)

			# average = np.average(frame)
			# if average < 2.6:
			#	continue
			# print(f'Using frame {index} (avg={average})')

			# x_corr, y_corr = self._get_offset_correction(self.image, frame, x, y, 10)
			# print(f'Frame {index}: Applying offset correction {x_corr}, {y_corr}')
			# x += x_corr
			# y += y_corr

			self.image[x:x+image_width, y:y+image_height, :] += frame
			self.samples[x:x+image_width, y:y+image_height] += 1

		if np.amin(self.image) < 0:
			print('An overflow occurred during stacking. Consider using --bits=32')
			sys.exit(1)

	@staticmethod
	def _get_offset_correction(image, frame, x_ofs, y_ofs, radius):
		width, height, channels = frame.shape
		best_sim = 0
		best_corr = (0, 0)

		frame_lin = frame.flatten().astype(float)
		frame_norm = np.linalg.norm(frame_lin)
		
		for x_corr in range(-radius, radius+1):
			for y_corr in range(-radius, radius+1):
				image_slice = image[x_ofs+x_corr:x_ofs+x_corr+width, y_ofs+y_corr:y_ofs+y_corr+height, :]
				if image_slice.shape != (width, height, channels):
					continue

				slice_lin = image_slice.flatten().astype(float)
				num = np.dot(slice_lin, frame_lin)
				denom = np.linalg.norm(slice_lin) * frame_norm
				if denom == 0:
					continue

				sim = num / denom
				if sim > best_sim:
					best_sim = sim
					best_corr = x_corr, y_corr

		return best_corr

	@staticmethod
	def _load_frame(filename, dtype, crop_input):
		pil_image = Image.open(filename)
		yxc_image = np.asarray(pil_image, dtype=dtype)
		xyc_image = np.transpose(yxc_image, (1, 0, 2))

		if crop_input is not None:
			cx, cy, r = crop_input.split(',')
			cx, cy, r = int(cx), int(cy), int(r)
			return xyc_image[cx-r:cx+r, cy-r:cy+r, :]

		return xyc_image

	@staticmethod
	def _interpolate_offsets(num_images, x_offset, y_offset):
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
