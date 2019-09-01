import json
import os
import sys
import numpy as np

from PIL import Image


class ImageStackNebula:

	def __init__(self, directory, files, bits):

		dtype = np.int16 if bits == 16 else np.int32

		# read offsets file
		offsets_file = os.path.join(directory, 'offsets.json')
		with open(offsets_file, 'r') as f:
			frame_offsets = json.load(f)

		# import pdb; pdb.set_trace()

		max_offset_x = int(max(x for x,_ in frame_offsets.values()))
		min_offset_x = int(min(x for x,_ in frame_offsets.values()))
		min_offset_y = int(min(y for _,y in frame_offsets.values()))
		max_offset_y = int(max(y for _,y in frame_offsets.values()))

		frame_0 = self._load_frame(files[0], dtype=dtype)
		width, height, channels = frame_0.shape

		output_width = width + abs(min_offset_x) + abs(max_offset_x)
		output_height = height + abs(min_offset_y) + abs(max_offset_y)

		self.image = np.zeros((output_width, output_height, channels), dtype=dtype)
		self.samples = np.zeros((output_width, output_height), dtype=np.int16)

		for filename, (offset_x,offset_y) in frame_offsets.items():

			filename = os.path.join(directory, filename)
			frame = self._load_frame(filename, dtype)

			# sharpness = self._get_sharpness(frame)
			# if sharpness < 1.73:
			# 	print(f'Discarding frame {index} because its sharpness is low')
			# 	continue

			x = int(offset_x)+abs(min_offset_x)
			y = int(offset_y)+abs(min_offset_y)

			self.image[x:x+width, y:y+height, :] += frame
			self.samples[x:x+width, y:y+height] += 1

		if np.amin(self.image) < 0:
			print('An overflow occurred during stacking. Consider using --bits=32')
			sys.exit(1)

	@staticmethod
	def _get_sharpness(xyc_image):
		xy_image = np.sum(xyc_image, axis=2)
		gy, gx = np.gradient(xy_image)
		gnorm = np.sqrt(gx**2 + gy**2)
		return np.average(gnorm)

	@staticmethod
	def _load_frame(filename, dtype):
		pil_image = Image.open(filename)
		yxc_image = np.asarray(pil_image, dtype=dtype)
		xyc_image = np.transpose(yxc_image, (1, 0, 2))
		return xyc_image

	def floatify(self):
		self.image = self.image.astype(float)

	def normalize(self):
		min_value = np.amin(self.image)
		max_value = np.amax(self.image)
		if max_value == 0:
			print('Not normalizing image: It is all black.')		
			return
		print(f'Normalizing brightness, min={min_value}, max={max_value}')

		if max_value > min_value:
			normalized = (self.image - min_value) / (max_value - min_value)
		else:
			normalized = (self.image - min_value)

		self.image = normalized

	def normalize_samples(self):
		min_samples = np.amin(self.samples)
		max_samples = np.amax(self.samples)
		if min_samples == 0:
			print('Not normalizing image: There are pixels without samples.')
			return
		print(f'Normalizing by number of samples, min={min_samples}, max={max_samples}')

		_w, _h, channels = self.image.shape
		for channel in range(channels):
			self.image[:,:,channel] = self.image[:,:,channel] * max_samples / self.samples

	def crop(self, cx, cy, r):
		# crop image to a square with center <cx,cy> and radius <>.
		self.image = self.image[cx-r:cx+r, cy-r:cy+r, :]
		self.samples = self.samples[cx-r:cx+r, cy-r:cy+r]

	def auto_crop(self, min_samples=None):
		width, height = self.samples.shape
		
		min_x, max_x, min_y, max_y = None, None, None, None
		for x in range(width):
			for y in range(height):
				if self.samples[x, y] >= min_samples:
					min_x = min(min_x or x, x)
					max_x = max(max_x or x, x)
					min_y = min(min_y or y, y)
					max_y = max(max_y or y, y)

		print(f'Cropping image to x=[{min_x},{max_x}], y=[{min_y},{max_y}]')
		self.image = self.image[min_x:max_x+1, min_y:max_y+1, :]
		self.samples = self.samples[min_x:max_x+1, min_y:max_y+1]

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

	def save_samples_map(self, filename, num_shades=8):
		out_image = self.samples * (256.0 / num_shades)
		yx_image = np.transpose(out_image, (1, 0))
		yx_image = yx_image.astype(np.uint8)
		pil_image = Image.fromarray(yx_image, mode='L')
		pil_image.save(filename)
