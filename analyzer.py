import os
import sys
import math
import json
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from skimage.feature import register_translation

from frame import Frame
from util import load_image_greyscale


class Analyzer:
	# Rotation, Flipping, Offset detection.

	def __init__(self, amplification=5, threshold=128):
		# factor by which brightness should be scaled up for alignment
		self.amplification = amplification
		# brightness threshold to apply before alignment
		self.threshold = threshold

		self.key_frame = None

		# map frame index to offsets-tuple
		self.frame_offsets = {0: (0,0)}

		self.frame_offsets_by_file = {}
		self.astrometric_metadata_by_file = {}

	def analyze(self, frame, frame_index):
		basename = os.path.basename(frame.filepath)
		self.astrometric_metadata_by_file[basename] = Frame.get_astrometric_metadata(frame.filepath)
		frame_image = load_image_greyscale(frame.filepath)
		self.frame_offsets_by_file[basename] = self.get_offsets(frame_image, frame_index)

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

	def write_astrometric_metadata(self, directory, filename='astrometric_metadata.json'): 
		filepath = os.path.join(directory, filename)
		with open(filepath, 'w') as f:
			json.dump(self.astrometric_metadata_by_file, f, indent=4, sort_keys=True)

	def write_offsets_file(self, directory, filename='offsets,json'):
		filepath = os.path.join(directory, filename)
		with open(filepath, 'w') as f:
			json.dump(self.frame_offsets_by_file, f, indent=4, sort_keys=True)

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

#
# Experimental: Detect blurry frames through offsets between runs of three frames
#
# def pairwise(iterable):
#     "s -> (s0,s1), (s1,s2), (s2, s3), ..."
#     a, b = itertools.tee(iterable)
#     next(b, None)
#     return zip(a, b)
# 
# def distance(p1, p2):
# 	return math.sqrt((p2[0]-p1[0])*(p2[0]-p1[0]) + (p2[1]-p1[1])*(p2[1]-p1[1]))
# 
# distances = [distance(p1, p2) for p1, p2 in pairwise(frame_offsets)]
# instability = [max(d1, d2) for d1, d2 in pairwise(distances)]
# 
# def runs(instability, thresh):
# 	below_thresh = [inst < thresh for inst in instability]
# 	# ...
# 
# print(instability)
# 
