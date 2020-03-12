import numpy as np

from skimage.feature import register_translation

from lib.util import load_image
from lib.tracker import Tracker


class ImageTracker(Tracker):
	def __init__(self, config, image_search_pattern, axis_control):
		super().__init__(config, image_search_pattern, axis_control)
		self.reference_image = None
		# parameters that help with image offset detection in bad conditions
		self.amplification = config['image_amplification']
		self.threshold = config['image_threshold']

	def on_new_file(self, filepath):

		# original frame - all color channels
		image = load_image(filepath, dtype=np.int16)
		# greyscale frame, only width and height
		image_greyscale = np.mean(image, axis=2)
		# the same, but optimized for offset-detection
		image_for_offset_detection = np.clip(image_greyscale * self.amplification, self.threshold, 255)

		if self.reference_image is None:
			print(f'Using reference image: {filepath}')
			self.reference_image = image_for_offset_detection
			return

		(ra_error, dec_error), _, __ = register_translation(self.reference_image, image_for_offset_detection)
		
		if ra_error == 0 and dec_error == 0:
			print(f'Image errors are (0,0) in {file_path}. Falling back to resting speed.')
			self.axis_control.set_motor_speed('A', AxisControl.ra_resting_speed)		
			self.axis_control.set_motor_speed('B', AxisControl.dec_resting_speed)
			return

		ra_speed = self.config['ra']['center'] + self.ra_pid(-ra_error if self.config['ra']['invert'] else ra_error)
		dec_speed = self.config['dec']['center'] + self.dec_pid(-dec_error if self.config['dec']['invert'] else dec_error)

		print(f'RA error: {ra_error:8.6f}, DEC error: {dec_error:8.6f}, '\
			  f'RA speed: {ra_speed:8.6f}, DEC speed: {dec_speed:8.6f}')
		
		if self.axis_control is not None:
			self.axis_control.set_motor_speed('A', ra_speed)		
			self.axis_control.set_motor_speed('B', dec_speed)

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
