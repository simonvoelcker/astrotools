import numpy as np

from skimage.feature import register_translation

from .periodic_error import ErrorSample
from .tracker import Tracker
from ..state.events import log_event


class PassiveTracker(Tracker):

	def __init__(self, config, axis_control, *args):
		super().__init__(config, axis_control, None)
		self.reference_image = None
		self.sigma_threshold = config['sigma_threshold']
		self.error_recorder = None

	def set_error_recorder(self, recorder):
		self.error_recorder = recorder

	def _clean_image_for_offset_detection(self, image):
		# greyscale frame, only width and height
		image_greyscale = np.mean(image, axis=2)
		stddev = np.std(image_greyscale)
		average = np.average(image_greyscale)
		threshold = self.sigma_threshold
		# clip away background noise, as indicated by stddev and average
		cleaned = np.clip(image_greyscale, average + threshold * stddev, 255)
		return cleaned

	def on_new_frame(self, frame):

		pil_image = frame.get_pil_image()
		image = np.transpose(np.asarray(pil_image), (1, 0, 2))
		image_for_offset_detection = self._clean_image_for_offset_detection(image)

		if self.reference_image is None:
			log_event(f'Using reference frame: {frame.path}')
			self.reference_image = image_for_offset_detection
			return

		(x_error, y_error), _, __ = register_translation(
			self.reference_image,
			image_for_offset_detection,
		)

		log_event(f'Tracking. File: {frame.path}. Errors: {(x_error, y_error)}')

		if self.error_recorder is not None and not self.error_recorder.done:
			ra_wheel_position = self.axis_control.get_ra_wheel_position()
			self.error_recorder.add_sample(
				ErrorSample(
					ra_wheel_position=ra_wheel_position,
					x_pixel_error=float(x_error),
					y_pixel_error=float(y_error),
				)
			)

		if self.influx_client is not None:
			self.write_frame_stats(
				file_path=frame.path,
				ra_image_error=float(x_error),
				dec_image_error=float(y_error),
			)
