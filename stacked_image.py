import sys
import numpy as np

from PIL import Image


class StackedImage:

	def __init__(self, files, x_offset, y_offset, stride, bits, crop_input):

		dtype = np.int16 if bits == 16 else np.int32

		image_0 = self._load_frame(files[0], dtype)

		cx, cy, r = crop_input.split(',')
		cx, cy, r = int(cx), int(cy), int(r)

		frame_0 = image_0[cx-r:cx+r, cy-r:cy+r, :]
		frame_width, frame_height, channels = frame_0.shape

		x_offset = -x_offset
		y_offset = -y_offset
		image_offsets = list(self._interpolate_offsets(len(files), x_offset, y_offset))

		frames = []
		for index, (x,y) in enumerate(image_offsets):
			if index % stride != 0:
				continue
			full_frame = self._load_frame(files[index], dtype)

			frame = full_frame[cx-r+x : cx+r+x, cy-r+y : cy+r+y, :]

			sharpness = self._get_sharpness(frame)
			#if sharpness < 0.465:
			#	print(f'Discarding frame {index} because its sharpness is low')
			#	continue

			max_offset = 6
			corr_x, corr_y = self._get_offset_correction(image_0, frame, cx-r+image_offsets[0][0], cy-r+image_offsets[0][1], max_offset, index)

			if abs(corr_x) == max_offset or abs(corr_y) == max_offset:
				print(f'Discarding frame {index} because its offset is too high ({corr_x}, {corr_y})')
				continue

			frame = full_frame[cx-r+x-corr_x : cx+r+x-corr_x, cy-r+y-corr_y : cy+r+y-corr_y, :]

			if frame.shape != (frame_width, frame_height, channels):
				print(f'Discarding frame {index} because shape is bad ({frame.shape})')
				continue

			print(f'Using frame {index}: corr={(corr_x, corr_y)}, sharpness={sharpness}')

			#composed_frame = np.zeros((2*frame_width, frame_height, channels), dtype=np.int8)
			#composed_frame[0*frame_width:1*frame_width, :, :] = full_frame[cx+x-r       :cx+x+r       , cy+y-r       :cy+y+r       , :]
			#composed_frame[1*frame_width:2*frame_width, :, :] = full_frame[cx+x-r-corr_x:cx+x+r-corr_x, cy+y-r-corr_y:cy+y+r-corr_y, :]
			#yxc_image = np.transpose(composed_frame, (1, 0, 2))
			#yxc_image = yxc_image.astype(np.int8)
			#pil_image = Image.fromarray(yxc_image, mode='RGB')
			#pil_image.save(f'frames_1/{index}.png')

			frames.append(frame)

		print(f'Stacking image from {len(frames)} frames')

		image_stack = np.zeros((frame_width, frame_height, channels, len(frames)), dtype=dtype)
		for index, frame in enumerate(frames):
			image_stack[:, :, :, index] = frame

		self.image = np.median(image_stack, axis=3)
		self.samples = np.ones((frame_width, frame_height), dtype=np.int16)

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
	def _get_offset_correction(image, frame, x_ofs, y_ofs, radius, index):
		width, height, channels = frame.shape
		best_sim = 0
		best_corr = (0, 0)

		frame_lin = frame.flatten().astype(float)
		frame_norm = np.linalg.norm(frame_lin)
		
		for x_corr in range(-radius, radius+1):
			for y_corr in range(-radius, radius+1):

				image_slice = image[x_ofs+x_corr:x_ofs+x_corr+width, y_ofs+y_corr:y_ofs+y_corr+height, :]
				
				#composed_frame = np.zeros((2*width, height, channels))
				#composed_frame[0*width:1*width, :, :] = image_slice
				#composed_frame[1*width:2*width, :, :] = frame
#
#				#yxc_image = np.transpose(composed_frame, (1, 0, 2))
#				#yxc_image = yxc_image.astype(np.int8)
#				#pil_image = Image.fromarray(yxc_image, mode='RGB')
#				#pil_image.save(f'frames_2/{index}.png')
#
				#return best_corr

				if image_slice.shape != (width, height, channels):
					print('WARN 1')
					continue

				slice_lin = image_slice.flatten().astype(float)
				num = np.dot(slice_lin, frame_lin)
				denom = np.linalg.norm(slice_lin) * frame_norm
				if denom == 0:
					print('WARN 2')
					continue

				sim = num / denom
				if sim > best_sim:
					best_sim = sim
					best_corr = x_corr, y_corr

		return best_corr

	@staticmethod
	def _load_frame(filename, dtype):
		pil_image = Image.open(filename)
		yxc_image = np.asarray(pil_image, dtype=dtype)
		xyc_image = np.transpose(yxc_image, (1, 0, 2))
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
