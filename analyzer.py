import os
import sys
import math
import json
import datetime
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from skimage.feature import register_translation
from influxdb import InfluxDBClient

from frame import Frame
from util import load_image_greyscale


class Analyzer:

	def __init__(self, amplification=1, threshold=128):
		# factor by which brightness should be scaled up for alignment
		self.amplification = amplification
		# brightness threshold to apply before alignment
		self.threshold = threshold

		self.offsets_reference_frame = None

		# map frames to frame metadata
		self.frame_offsets = {}
		self.astrometric_metadata = {}
		self.frame_brightness = {}

	def get_astrometric_metadata_hint(self):
		for metadata in self.astrometric_metadata.values():
			if metadata is not None:
				return {
					'ra': metadata['center_deg']['ra'],
					'dec': metadata['center_deg']['dec'],
					'radius': 1.0,
				}
		return None

	def analyze(self, frame):
		hint = self.get_astrometric_metadata_hint()
		self.astrometric_metadata[frame] = frame.compute_astrometric_metadata(hint)
		self.frame_offsets[frame] = self.get_offsets(frame)
		self.frame_brightness[frame] = np.average(load_image_greyscale(frame.filepath))

	def get_offsets(self, frame):
		frame_image = load_image_greyscale(frame.filepath)
		# apply measures to improve offset detection on our kind of images
		curr_frame = np.clip(frame_image * self.amplification, self.threshold, 255)

		if self.offsets_reference_frame is None:
			self.offsets_reference_frame = curr_frame
			return 0, 0

		(offset_x, offset_y), error, _ = register_translation(self.offsets_reference_frame, curr_frame)
		return (offset_x, offset_y)

	def write_astrometric_metadata(self, directory, filename='astrometric_metadata.json'): 
		filepath = os.path.join(directory, filename)
		metadata_by_file = {
			os.path.basename(frame.filepath): metadata
			for frame, metadata in self.astrometric_metadata.items()
		}
		with open(filepath, 'w') as f:
			json.dump(metadata_by_file, f, indent=4, sort_keys=True)

	def write_offsets_file(self, directory, filename='offsets.json'):
		filepath = os.path.join(directory, filename)
		offsets_by_file = {
			os.path.basename(frame.filepath): offsets
			for frame, offsets in self.frame_offsets.items()
		}
		with open(filepath, 'w') as f:
			json.dump(offsets_by_file, f, indent=4, sort_keys=True)

	def create_offsets_plot(self, filename='offsets_plot.png'):
		x_offsets = np.array([x for x,y in self.frame_offsets.values()])
		y_offsets = np.array([y for x,y in self.frame_offsets.values()])

		colors = (0,0,0)
		area = np.pi*3

		plt.scatter(x_offsets, y_offsets, s=area, c=colors, alpha=0.5)
		plt.title('Frame offsets')
		plt.xlabel('x')
		plt.ylabel('y')
		plt.savefig(filename)

	def write_to_influx(self):
		influx_client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='tracking')

		frames = list(self.frame_offsets.keys())

		frame_0_time_posix = os.path.getctime(frames[0].filepath)
		exposure = 15

		for frame_index, frame in enumerate(frames):
			frame_time_posix = frame_0_time_posix + frame_index * exposure
			frame_time = datetime.datetime.utcfromtimestamp(frame_time_posix).strftime('%Y-%m-%dT%H:%M:%S%Z')
			print(f'Frame {os.path.basename(frame.filepath)}: Time={frame_time}')

			fields = {
				'filepath': frame.filepath,
				'basename': os.path.basename(frame.filepath),
				'time_posix': float(frame_time_posix),
			}
			metadata = self.astrometric_metadata[frame]
			if metadata is not None:
				fields.update({
					'center_ra': metadata['center']['ra'],
					'center_dec': metadata['center']['dec'],
					'center_ra_deg': float(metadata['center_deg']['ra']),
					'center_dec_deg': float(metadata['center_deg']['dec']),
					'parity': bool(metadata['parity']['parity'] == 'pos'),
					'pixel_scale': float(metadata['pixel_scale']['scale']),
					'pixel_scale_unit': metadata['pixel_scale']['unit'],
					'rotation_angle': float(metadata['rotation']['angle']),
					'rotation_direction': metadata['rotation']['direction'],
					'size_width': float(metadata['size']['width']),
					'size_height': float(metadata['size']['height']),
					'size_unit': metadata['size']['unit'],
					'offset_x': float(self.frame_offsets[frame][0]),
					'offset_y': float(self.frame_offsets[frame][1]),
					'brightness': float(self.frame_brightness[frame]),
				})

			body = [
			    {
			        'measurement': 'frame_stats',
			        'tags': {
			            'source': 'analyzer.py',
			        },
			        'time': frame_time,
			        'fields': fields, 
			    }
			]
			influx_client.write_points(body)

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
