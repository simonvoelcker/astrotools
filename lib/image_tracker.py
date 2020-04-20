import numpy as np
import numpy.ma as ma

from skimage.feature import register_translation

from lib.axis_control import AxisControl
from lib.util import load_image, sigma_clip_dark_end
from lib.tracker import Tracker


class ImageTracker(Tracker):
 
	def __init__(self, config, axis_control):
		super().__init__(config, axis_control)
		self.reference_image = None
		self.sigma_threshold = config['sigma_threshold']

	def on_new_file(self, filepath):
		image = load_image(filepath, dtype=np.int16)
		image_for_offset_detection = sigma_clip_dark_end(image, self.sigma_threshold)

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
