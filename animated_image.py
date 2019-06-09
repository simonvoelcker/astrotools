import sys
import numpy as np

from PIL import Image


class AnimatedImage:

	def __init__(self, files, x_offset, y_offset, stride, bits, cx, cy, r):

		dtype = np.int16 if bits == 16 else np.int32

		image_offsets = self._interpolate_offsets(len(files), x_offset, y_offset)
		self.frames = []

		for index, (x,y) in enumerate(image_offsets):
			if index % stride != 0:
				continue
			frame = self._load_frame(files[index], dtype)
			frame = frame[x+cx-r:x+cx+r, y+cy-r:y+cy+r, :]

			avg = np.average(frame)
			if avg >= 5.3:
				self.frames.append(frame)

		print(len(self.frames))

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
		self.frames = [
			frame.astype(float) / 255.0
			for frame in self.frames
		]

	def save(self, filename):
		# (1) need to pick R channel and store as greyscale

		pil_images = []
		for index, frame in enumerate(self.frames):
			out_image = 255.0 * frame
			yxc_image = np.transpose(out_image, (1, 0, 2))
			yxc_image = yxc_image.astype(np.int8)[:,:,0]
			pil_image = Image.fromarray(yxc_image, mode='L')
			pil_images.append(pil_image)

			pil_image.save(f'frames/frame_{index}.png')
		
		pil_images[0].save(filename, save_all=True, append_images=pil_images[1:], duration=80, loop=0)
