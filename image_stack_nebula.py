import json
import os
import sys
import numpy as np
import math

from PIL import Image
from skimage.transform import rotate 
from frame import Frame


class ImageStackNebula:

	def __init__(self, image, samples):
		self.image = image
		self.samples = samples

	@classmethod
	def create_average_frame(cls, directory, files, color_mode):
		frame_0 = cls._load_frame(files[0], dtype=np.int32, color_mode=color_mode)
		width, height, channels = frame_0.shape

		image = np.zeros((width, height, channels), dtype=float)

		for filename in files:
			frame = cls._load_frame(filename, dtype=float, color_mode=color_mode)
			image[:, :, :] += frame

		image /= float(len(files))
		image = np.clip(image, 0.0, 255.0)
		return image

	@classmethod
	def from_files(cls, directory, files, offsets, color_mode, master_dark, master_flat):
		# old method which is using a dict mapping file basename to x,y offsets (pixels)

		max_offset_x = int(max(x for x,_ in offsets.values()))
		min_offset_x = int(min(x for x,_ in offsets.values()))
		min_offset_y = int(min(y for _,y in offsets.values()))
		max_offset_y = int(max(y for _,y in offsets.values()))

		frame_0 = cls._load_frame(files[0], dtype=np.int32, color_mode=color_mode)
		width, height, channels = frame_0.shape

		output_width = width + abs(min_offset_x) + abs(max_offset_x)
		output_height = height + abs(min_offset_y) + abs(max_offset_y)

		image = np.zeros((output_width, output_height, channels), dtype=float)
		samples = np.zeros((output_width, output_height), dtype=np.int16)

		for filename in files:
			filename = os.path.basename(filename)
			offset_x, offset_y = offsets[filename]

			filepath = os.path.join(directory, filename)
			frame = cls._load_frame(filepath, dtype=float, color_mode=color_mode)

			if master_dark is not None:
				frame -= master_dark
			if master_flat is not None:
				frame /= master_flat

			x = int(offset_x)+abs(min_offset_x)
			y = int(offset_y)+abs(min_offset_y)

			image[x:x+width, y:y+height, :] += frame
			samples[x:x+width, y:y+height] += 1

		return ImageStackNebula(image, samples)


	@classmethod
	def stack_frames(cls, frames, color_mode, master_dark, master_flat):
		# seems to differ a little between frames, must average
		pixel_scales = [frame.pixel_scale for frame in frames]
		average_pixel_scale_aspp = sum(pixel_scales) / len(pixel_scales)

		reference_frame = frames[0]
		offsets = {
			frame: frame.get_pixel_offset(reference_frame, average_pixel_scale_aspp)
			for frame in frames
		}

		max_offset_x = int(max(x for x,_ in offsets.values()))
		min_offset_x = int(min(x for x,_ in offsets.values()))
		min_offset_y = int(min(y for _,y in offsets.values()))
		max_offset_y = int(max(y for _,y in offsets.values()))

		frame_0 = cls._load_frame(frames[0].filepath, dtype=np.int32, color_mode=color_mode)
		width, height, channels = frame_0.shape

		output_width = width + abs(min_offset_x) + abs(max_offset_x)
		output_height = height + abs(min_offset_y) + abs(max_offset_y)

		image = np.zeros((output_width, output_height, channels), dtype=float)
		samples = np.zeros((output_width, output_height), dtype=np.int16)

		for frame in frames:
			offset_x, offset_y = offsets[frame]
			frame_image = cls._load_frame(frame.filepath, dtype=float, color_mode=color_mode)

			if master_dark is not None:
				frame_image -= master_dark
			if master_flat is not None:
				frame_image /= master_flat

			frame_image = rotate(frame_image, frame.angle)

			x = int(offset_x) + abs(min_offset_x)
			y = int(offset_y) + abs(min_offset_y)

			image[x:x+width, y:y+height, :] += frame_image
			samples[x:x+width, y:y+height] += 1

		return ImageStackNebula(image, samples)

	@classmethod
	def from_frames_old(cls, frames, offsets):
		max_offset_x = int(max(x for x,_ in offsets))
		min_offset_x = int(min(x for x,_ in offsets))
		min_offset_y = int(min(y for _,y in offsets))
		max_offset_y = int(max(y for _,y in offsets))
		
		width, height, channels = frames[0].shape
	
		output_width = width + abs(min_offset_x) + abs(max_offset_x)
		output_height = height + abs(min_offset_y) + abs(max_offset_y)

		image = np.zeros((output_width, output_height, channels), dtype=float)
		samples = np.zeros((output_width, output_height), dtype=np.int16)

		for frame, (offset_x,offset_y) in zip(frames, offsets):

			x = int(offset_x)+abs(min_offset_x)
			y = int(offset_y)+abs(min_offset_y)

			image[x:x+width, y:y+height, :] += frame
			samples[x:x+width, y:y+height] += 1

		return ImageStackNebula(image, samples)

	@staticmethod
	def _get_sharpness(xyc_image):
		xy_image = np.sum(xyc_image, axis=2)
		gy, gx = np.gradient(xy_image)
		gnorm = np.sqrt(gx**2 + gy**2)
		return np.average(gnorm)

	@staticmethod
	def _load_frame(filename, dtype, color_mode='rgb'):
		pil_image = Image.open(filename)
		yxc_image = np.asarray(pil_image, dtype=dtype)
		xyc_image = np.transpose(yxc_image, (1, 0, 2))

		if color_mode == 'r':
			xyc_image = np.expand_dims(xyc_image[:,:,0], axis=2)
		elif color_mode == 'g':
			xyc_image = np.expand_dims(xyc_image[:,:,1], axis=2)
		elif color_mode == 'b':
			xyc_image = np.expand_dims(xyc_image[:,:,2], axis=2)
		elif color_mode == 'grey':
			grayscale_image = xyc_image[:,:,0] / 3 + xyc_image[:,:,1] / 3 + xyc_image[:,:,2] / 3 
			xyc_image = np.expand_dims(grayscale_image, axis=2)

		return xyc_image

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

		inset = 50
		min_x += inset
		max_x -= inset
		min_y += inset
		max_y -= inset

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

		if yxc_image.shape[2] == 1:
			# expand image to three equal channels
			expanded_image = np.zeros((yxc_image.shape[0], yxc_image.shape[1], 3), dtype=np.int8)
			expanded_image[:,:,0] = yxc_image[:,:,0]
			expanded_image[:,:,1] = yxc_image[:,:,0]
			expanded_image[:,:,2] = yxc_image[:,:,0]
			yxc_image = expanded_image

		pil_image = Image.fromarray(yxc_image, mode='RGB')
		pil_image.save(filename)

	def save_samples_map(self, filename, num_shades=8):
		out_image = self.samples * (256.0 / num_shades)
		yx_image = np.transpose(out_image, (1, 0))
		yx_image = yx_image.astype(np.uint8)
		pil_image = Image.fromarray(yx_image, mode='L')
		pil_image.save(filename)
		