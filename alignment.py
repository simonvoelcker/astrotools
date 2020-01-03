import math
import numpy as np
import os
import sys
import matplotlib.pyplot as plt

from PIL import Image

from skimage.feature import register_translation


class Alignment:
	# Rotation, Flipping, Offset detection.

	def __init__(self, amplification=5, threshold=128):
		# factor by which brightness should be scaled up for alignment
		self.amplification = amplification
		# brightness threshold to apply before alignment
		self.threshold = threshold

		self.key_frame = None

		# map frame index to offsets-tuple
		self.frame_offsets = {0: (0,0)}

	def get_offsets(self, frame, frame_index):
		# apply measures to improve offset detection on our kind of images
		# TODO use those sneaky sigma-tricks from the astrometry guys
		curr_frame = np.clip(frame * self.amplification, self.threshold, 255)

		if frame_index == 0:
			self.key_frame = curr_frame
			return (0,0)

		(offset_x, offset_y), error, _ = register_translation(self.key_frame, curr_frame)
		offsets = (offset_x, offset_y)
		self.frame_offsets[frame_index] = offsets
		return offsets

	def create_plot(self, title, filename):
		x_offsets = np.array([x for _, (x,y) in self.frame_offsets.items()])
		y_offsets = np.array([y for _, (x,y) in self.frame_offsets.items()])

		colors = (0,0,0)
		area = np.pi*3

		plt.scatter(x_offsets, y_offsets, s=area, c=colors, alpha=0.5)
		plt.title(title)
		plt.xlabel('x')
		plt.ylabel('y')
		plt.savefig(filename)
