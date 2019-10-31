import numpy as np

from image_stack_nebula import ImageStackNebula


class Preview:
	def __init__(self, num_frames):
		self.num_frames = num_frames
		self.frames = []
		self.offsets = []

	def update(self, frame, offset):
		self.frames = ([frame] + self.frames)[:self.num_frames]
		self.offsets = ([offset] + self.offsets)[:self.num_frames]
		self.stack_and_save()

	def stack_and_save(self):
		preview = ImageStackNebula.from_frames(self.frames, self.offsets)
		preview.auto_crop(np.amax(preview.samples))
		preview.floatify()
		preview.convert_to_grayscale()
		preview.normalize_samples()
		preview.normalize()
		preview.apply_gamma(0.3)
		preview.save('preview.png')
