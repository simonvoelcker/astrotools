import json
import os
import sys
import numpy as np

from PIL import Image


class ImageStackNebula:

	def __init__(self, image, samples):
		self.image = image
		self.samples = samples

	@classmethod
	def from_files(cls, directory, files, bits):
		dtype = np.int16 if bits == 16 else np.int32

		# read offsets file
		offsets_file = os.path.join(directory, 'offsets.json')
		with open(offsets_file, 'r') as f:
			frame_offsets = json.load(f)

		max_offset_x = int(max(x for x,_ in frame_offsets.values()))
		min_offset_x = int(min(x for x,_ in frame_offsets.values()))
		min_offset_y = int(min(y for _,y in frame_offsets.values()))
		max_offset_y = int(max(y for _,y in frame_offsets.values()))

		frame_0 = cls._load_frame(files[0], dtype=dtype)
		width, height, channels = frame_0.shape

		output_width = width + abs(min_offset_x) + abs(max_offset_x)
		output_height = height + abs(min_offset_y) + abs(max_offset_y)

		image = np.zeros((output_width, output_height, channels), dtype=dtype)
		samples = np.zeros((output_width, output_height), dtype=np.int16)

		for filename, (offset_x,offset_y) in frame_offsets.items():

			filename = os.path.join(directory, filename)
			frame = cls._load_frame(filename, dtype)

			x = int(offset_x)+abs(min_offset_x)
			y = int(offset_y)+abs(min_offset_y)

			image[x:x+width, y:y+height, :] += frame
			samples[x:x+width, y:y+height] += 1

		if np.amin(image) < 0:
			print('An overflow occurred during stacking. Consider using --bits=32')
			sys.exit(1)

		return ImageStackNebula(image, samples)

	@classmethod
	def from_frames(cls, frames, offsets, bits):
		dtype = np.int16 if bits == 16 else np.int32

		max_offset_x = int(max(x for x,_ in offsets))
		min_offset_x = int(min(x for x,_ in offsets))
		min_offset_y = int(min(y for _,y in offsets))
		max_offset_y = int(max(y for _,y in offsets))
		
		width, height, channels = frames[0].shape
	
		output_width = width + abs(min_offset_x) + abs(max_offset_x)
		output_height = height + abs(min_offset_y) + abs(max_offset_y)

		image = np.zeros((output_width, output_height, channels), dtype=dtype)
		samples = np.zeros((output_width, output_height), dtype=np.int16)

		for frame, (offset_x,offset_y) in zip(frames, offsets):

			x = int(offset_x)+abs(min_offset_x)
			y = int(offset_y)+abs(min_offset_y)

			image[x:x+width, y:y+height, :] += frame
			samples[x:x+width, y:y+height] += 1

		if np.amin(image) < 0:
			print('An overflow occurred during stacking. Consider using --bits=32')
			sys.exit(1)

		return ImageStackNebula(image, samples)

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
		print('Converting image to float')
		self.image = self.image.astype(float)

	def convert_to_grayscale(self):
		print('Converting image to greyscale (ghetto style)')
		grayscale_image = self.image[:,:,0] / 3 + self.image[:,:,1] / 3 + self.image[:,:,2] / 3 
		self.image[:,:,0] = grayscale_image
		self.image[:,:,1] = grayscale_image
		self.image[:,:,2] = grayscale_image

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

	def normalize_histogram(self, num_bins=256):
		print(f'Normalizing histogram, using {num_bins} bins')
		unique_values = np.unique(self.image)
		num_unique_values = len(unique_values)
		histogram = np.histogram(self.image, bins=num_unique_values)

		# histogram = (<bin sizes>, <color value>)
		num_values = sum(histogram[0])
		
		num_out_bins = num_bins
		out_bin_size = num_values / num_out_bins

		out_bins = []

		cum_bin_size = 0
		for bin_size, color_value in zip(*histogram):
			cum_bin_size += bin_size
			if cum_bin_size >= out_bin_size:
				# produce a bin
				out_bins.append(color_value)
				cum_bin_size = 0 #-= out_bin_size
				#print(out_bin_size, cum_bin_size)

		if len(out_bins) != num_out_bins:
			print(f'Error. Out bins={len(out_bins)}, expected {num_out_bins}')
			return
		#if cum_bin_size != 0:
		#	print(f'Error. Remaining cumulative bin size is {cum_bin_size} after bin creation')
		#	return

		bin_from_value = dict()
		for value in unique_values:
			bin_found = False
			for bin_index, bin_value in enumerate(out_bins):
				if bin_value >= value:
					bin_from_value[value] = bin_index
					bin_found = True
					break
			if not bin_found:
				bin_from_value[value] = len(out_bins)-1

		def bin_index(value):
			return bin_from_value[value]

		self.apply_function(bin_index)

	def clamp_outliers(self, shades):
		# TODO restore this when needed

		unique_values = np.unique(self.image)
		if len(unique_values) < 2*shades+1:
			print(f'Not enough different colors in the image to clamp outliers.')
			return
		print(f'Clamping outliers. Found {len(unique_values)} unique color values')

		# we will need negative indexing to get the n highest values
		unique_values = list(unique_values)

		def clamp(value):
			if value == 0:
				return 0.5
			#if value > unique_values[-shades]:
			#	return unique_values[-shades]
			return value

		self.apply_function(clamp)

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

	def apply_function(self, f):
		self.image = np.vectorize(f)(self.image)

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
