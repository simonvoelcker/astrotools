import numpy as np
import os

from skimage.feature import register_translation

from lib.util import load_image
from lib.solver import Solver
from lib.tracker import Tracker


class PassiveTracker(Tracker):

	def __init__(self, config, *args):
		super().__init__(config, None, None)
		self.reference_image = None
		self.reference_coordinates = None
		self.sigma_threshold = config['sigma_threshold']

	def _clean_image_for_offset_detection(self, image):
		# greyscale frame, only width and height
		image_greyscale = np.mean(image, axis=2)
		stddev = np.std(image_greyscale)
		average = np.average(image_greyscale)
		threshold = self.sigma_threshold
		# clip away background noise, as indicated by stddev and average
		cleaned = np.clip(image_greyscale, average + threshold * stddev, 255)
		return cleaned

	def on_new_frame(self, frame, path_prefix, status_change_callback=None):
		filepath = os.path.join(path_prefix, frame.path)
		image = load_image(filepath, dtype=np.int16)
		image_for_offset_detection = self._clean_image_for_offset_detection(image)

		if self.reference_image is None:
			status_change_callback(message='Using reference frame', filepath=filepath)
			self.reference_image = image_for_offset_detection
			self.reference_coordinates = Solver().locate_image(filepath, timeout=5)
			if not self.reference_coordinates:
				status_change_callback(message='Failed to determine coordinates of reference frame', filepath=filepath)
			return

		(ra_error, dec_error), _, __ = register_translation(self.reference_image, image_for_offset_detection)
		
		ra_coord_error = None
		dec_coord_error = None
		if self.reference_coordinates:
			coordinates = Solver().locate_image(filepath, timeout=5)
			if coordinates:
				ra_coord_error = coordinates.ra - self.reference_coordinates.ra
				dec_coord_error = coordinates.dec - self.reference_coordinates.dec
				status_change_callback(
					message='Tracking',
					filepath=filepath,
					errors=(ra_error, dec_error),
					coord_errors=(ra_coord_error, dec_coord_error)
				)
			else:
				status_change_callback(message='Tracking', filepath=filepath, errors=(ra_error, dec_error))
		else:
			status_change_callback(message='Tracking', filepath=filepath, errors=(ra_error, dec_error))

		if self.influx_client is not None:
			self.write_frame_stats(
				file_path=filepath,
				ra_image_error=float(ra_error),
				dec_image_error=float(dec_error),
				ra_coord_error=float(ra_coord_error or 0.0),
				dec_coord_error=float(dec_coord_error or 0.0),
			)
