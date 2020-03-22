import numpy as np
import numpy.ma as ma

from skimage.feature import register_translation

from lib.axis_control import AxisControl
from lib.util import load_image, save_image_greyscale
from lib.tracker import Tracker


class ImageTracker(Tracker):

	# TODO move image_sear_pattern to config as well

	def __init__(self, config, image_search_pattern, axis_control):
		super().__init__(config, image_search_pattern, axis_control)
		self.reference_image = None
		# parameters that help with image offset detection in bad conditions
		self.amplification = config['image_amplification']
		self.threshold = config['image_threshold']
		self.sigma_threshold = config['sigma_threshold']

	def _filter_image(self, image):
		# greyscale frame, only width and height
		image_greyscale = np.mean(image, axis=2)
		# stretch and clip
		return np.clip(image_greyscale * self.amplification, self.threshold, 255)

	def _filter_image_sigma_threshold(self, image, threshold):
		# greyscale frame, only width and height
		image_greyscale = np.mean(image, axis=2)
		stddev = np.std(image_greyscale)
		average = np.average(image_greyscale)
		# clip away background noise, as indicated by stddev and average
		cleaned = np.clip(image_greyscale, average + threshold * stddev, 255)
		# print(f'avg={average:.1f}, stddev={stddev:.1f}, thresh={threshold} => clipping {(average + threshold * stddev):.1f}-255')
		return cleaned

	def on_new_file(self, filepath):
		image = load_image(filepath, dtype=np.int16)
		image_for_offset_detection = self._filter_image_sigma_threshold(image, threshold=self.sigma_threshold)

		if self.reference_image is None:
			print(f'Using reference image: {filepath}')
			self.reference_image = image_for_offset_detection
			return

		(ra_error, dec_error), _, __ = register_translation(self.reference_image, image_for_offset_detection)
		
		if ra_error == 0 and dec_error == 0:
			print(f'Image errors are (0,0) in {filepath}. Falling back to resting speed.')
			self.axis_control.set_motor_speed('A', AxisControl.ra_resting_speed, quiet=True)		
			self.axis_control.set_motor_speed('B', AxisControl.dec_resting_speed, quiet=True)
			return

		ra_speed = self.config['ra']['center'] + self.ra_pid(-ra_error if self.config['ra']['invert'] else ra_error)
		dec_speed = self.config['dec']['center'] + self.dec_pid(-dec_error if self.config['dec']['invert'] else dec_error)

		print(f'RA error: {ra_error:8.6f}, RA speed: {ra_speed:8.6f}, '\
			  f'DEC error: {dec_error:8.6f}, DEC speed: {dec_speed:8.6f}')
		
		if self.axis_control is not None:
			self.axis_control.set_motor_speed('A', ra_speed, quiet=True)
			self.axis_control.set_motor_speed('B', dec_speed, quiet=True)

		if self.influx_client is not None:
			self.write_frame_stats(
				file_path=filepath,
				ra_image_error=float(ra_error),
				ra_speed=float(ra_speed),
				ra_pid_p=float(self.ra_pid.components[0]),
				ra_pid_i=float(self.ra_pid.components[1]),
				ra_pid_d=float(self.ra_pid.components[2]),
				dec_image_error=float(dec_error),
				dec_speed=float(dec_speed),
				dec_pid_p=float(self.dec_pid.components[0]),
				dec_pid_i=float(self.dec_pid.components[1]),
				dec_pid_d=float(self.dec_pid.components[2]),
			)
