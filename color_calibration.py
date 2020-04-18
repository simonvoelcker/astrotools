import argparse
import json
import numpy as np
from itertools import tee

from lib.util import load_image, save_image


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class ColorCalibrator:
	def __init__(self, config_file):
		with open(config_file) as f:
			config = json.load(f)
		# lookup table: channel, input_value => output value
		self.value_mapping = np.zeros((3, 256), dtype=float)

		for channel, channel_name in enumerate(("red", "green", "blue")):
			# make it an array of pairs for easier lookup
			input_values = sorted([value for value in config[channel_name].keys()])
			mapping_pairs = [(int(value), config[channel_name][value]) for value in input_values]

			channel_mapping = [self._map_value(mapping_pairs, value) for value in range(256)]
			self.value_mapping[channel,:] = channel_mapping

	def _map_value(self, mapping_pairs, value):
		for this_pair, next_pair in pairwise(mapping_pairs):
			if this_pair[0] <= value and next_pair[0] >= value:
				lerp = float(value - this_pair[0]) / (next_pair[0] - this_pair[0])		
				return this_pair[1] * (1.0 - lerp) + next_pair[1] * lerp
		raise RuntimeError(f'Failed to map value {value} using pairs {mapping_pairs}')

	def apply(self, image):
		def red_mapping(value):
			return self.value_mapping[0, value]
		def green_mapping(value):
			return self.value_mapping[1, value]
		def blue_mapping(value):
			return self.value_mapping[2, value]

		image[:,:,0] = np.vectorize(red_mapping)(image[:,:,0])
		image[:,:,1] = np.vectorize(green_mapping)(image[:,:,1])
		image[:,:,2] = np.vectorize(blue_mapping)(image[:,:,2])
		return image


parser = argparse.ArgumentParser()
parser.add_argument('filename', type=str)
args = parser.parse_args()

image = load_image(args.filename)
calibrated = ColorCalibrator('color_calibration.json').apply(image)
save_image(image, 'calibrated.png')
