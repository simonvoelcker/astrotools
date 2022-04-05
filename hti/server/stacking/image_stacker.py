from typing import List
from io import BytesIO

from lib.frame import Frame

import numpy as np

from PIL import Image
from skimage.transform import rotate 


class ImageStacker:

	def __init__(self):
		self.light_frames: List[Frame] = []

		self.color_mode = "rgb"

		# np array of the result of stacking
		self.stacked_image = None
		# np array with per-pixel sample counts used for normalization
		self.samples = None

		self.average_darkframe = None
		self.average_flatframe = None

	def get_stacked_image_hash(self) -> str:
		"""
		Get a hash of all the parameters that went into stacked_image
		so we can be smart about re-stacking and fetching the updated
		result only if any settings changed.
		"""
		# TODO crazy stupid hashing
		return str(len(self.light_frames))

	@staticmethod
	def normalize_image(image):
		"""
		Fit dynamic range found in the given image into [0;1].
		"""
		normalized_image = np.zeros(image.shape, dtype=image.dtype)

		for channel in range(image.shape[2]):
			min_value = np.amin(image[:, :, channel])
			max_value = np.amax(image[:, :, channel])
			if max_value == 0:
				print(f'Skipping channel {channel} in normalization')
				continue
			print(f'Normalizing channel {channel}, min={min_value:.1f}, max={max_value:.1f}')

			if max_value > min_value:
				normalized_image[:, :, channel] = (image[:, :, channel] - min_value) / (max_value - min_value)
			else:
				normalized_image[:, :, channel] = (image[:, :, channel] - min_value)

		return normalized_image

	def get_pil_image(self) -> Image:

		image = self.normalize_image(self.stacked_image)
		image = (255.0 * image)
		image = np.transpose(image, (1, 0, 2))
		image = image.astype(np.int8)

		# TODO find a better solution for greyscale
		if image.shape[2] == 1:
			# expand image to three equal channels
			expanded_image = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.int8)
			expanded_image[:, :, 0] = image[:, :, 0]
			expanded_image[:, :, 1] = image[:, :, 0]
			expanded_image[:, :, 2] = image[:, :, 0]
			image = expanded_image

		if image.ndim == 3:
			return Image.fromarray(image, mode='RGB')
		else:
			return Image.fromarray(image, mode='L')

	def get_stacked_image(
		self, format: str = 'png', scale_factor: int = 1
	) -> BytesIO:
		"""
		Get the stacked image for display purposes.
		"""
		image: Image = self.get_pil_image()

		if scale_factor != 1:
			width, height = image.width, image.height
			width //= scale_factor
			height //= scale_factor
			image = image.resize(size=(width, height), resample=Image.NEAREST)

		image_data = BytesIO()
		image.save(image_data, format=format)
		image_data.seek(0)
		return image_data

	@classmethod
	def create_average_frame(cls, files: List[str], color_mode: str):
		frame_0 = cls._load_frame(files[0], dtype=np.int32, color_mode=color_mode)
		width, height, channels = frame_0.shape

		image = np.zeros((width, height, channels), dtype=float)

		for filename in files:
			frame = cls._load_frame(filename, dtype=float, color_mode=color_mode)
			image[:, :, :] += frame

		image /= float(len(files))
		image = np.clip(image, 0.0, 255.0)
		return image

	def stack_image(self):
		frames = self.light_frames
		max_offset_x = max(frame.pixel_offset[0] for frame in frames)
		max_offset_y = max(frame.pixel_offset[1] for frame in frames)

		frame_0 = self._load_frame(
			frames[0].filepath, dtype=np.int32, color_mode=self.color_mode
		)
		width, height, channels = frame_0.shape

		output_width = width + max_offset_x
		output_height = height + max_offset_y

		image = np.zeros((output_width, output_height, channels), dtype=float)
		samples = np.zeros((output_width, output_height), dtype=float)

		for frame in frames:
			frame_image = self._load_frame(
				frame.filepath, dtype=float, color_mode=self.color_mode
			)
			samples_image = np.ones((width, height), dtype=float)

			if self.average_darkframe:
				frame_image -= self.average_darkframe
			if self.average_flatframe:
				frame_image /= self.average_flatframe

			frame_image = rotate(frame_image, frame.angle)
			samples_image = rotate(samples_image, frame.angle)

			x, y = frame.pixel_offset
			image[x:x+width, y:y+height, :] += frame_image
			samples[x:x+width, y:y+height] += samples_image

		for channel in range(channels):
			c = image[:, :, channel]
			image[:, :, channel] = np.divide(
				c, samples, out=np.zeros_like(c), where=samples != 0
			)

		self.stacked_image = image
		self.samples = samples

	@staticmethod
	def _load_frame(filename, dtype, color_mode='rgb'):
		pil_image = Image.open(filename)
		np_image = np.asarray(pil_image, dtype=dtype)

		if np_image.ndim == 3:
			xyc_image = np.transpose(np_image, (1, 0, 2))
		else:
			grayscale_image = np.transpose(np_image, (1, 0))
			grayscale_image = np.flipud(grayscale_image)
			xyc_image = np.expand_dims(grayscale_image, axis=2)
			# color mode does not make sense if image is grayscale from the start
			return xyc_image

		if color_mode == 'r':
			xyc_image = np.expand_dims(xyc_image[:, :, 0], axis=2)
		elif color_mode == 'g':
			xyc_image = np.expand_dims(xyc_image[:, :, 1], axis=2)
		elif color_mode == 'b':
			xyc_image = np.expand_dims(xyc_image[:, :, 2], axis=2)
		elif color_mode == 'grey':
			grayscale_image = (
				xyc_image[:, :, 0] * 0.21 +
				xyc_image[:, :, 1] * 0.72 +
				xyc_image[:, :, 2] * 0.07
			)
			xyc_image = np.expand_dims(grayscale_image, axis=2)

		return xyc_image

	def save(self, filename):
		out_image = (255.0 * self.stacked_image)
		yxc_image = np.transpose(out_image, (1, 0, 2))
		yxc_image = yxc_image.astype(np.int8)

		if yxc_image.shape[2] == 1:
			# expand image to three equal channels
			expanded_image = np.zeros(
				(yxc_image.shape[0], yxc_image.shape[1], 3), dtype=np.int8
			)
			expanded_image[:, :, 0] = yxc_image[:, :, 0]
			expanded_image[:, :, 1] = yxc_image[:, :, 0]
			expanded_image[:, :, 2] = yxc_image[:, :, 0]
			yxc_image = expanded_image

		pil_image = Image.fromarray(yxc_image, mode='RGB')
		pil_image.save(filename)

	def save_samples_map(self, filename, num_shades=8):
		out_image = self.samples * (256.0 / num_shades)
		yx_image = np.transpose(out_image, (1, 0))
		yx_image = yx_image.astype(np.uint8)
		pil_image = Image.fromarray(yx_image, mode='L')
		pil_image.save(filename)
