import os
import math
import subprocess
import re


class Frame:

	def __init__(self, filepath, metadata=None):
		self.filepath = filepath
		self.metadata = metadata

	@property
	def center(self):
		center_deg = self.metadata['center_deg']
		return float(center_deg['ra']), float(center_deg['dec'])

	@property
	def angle(self):
		return float(self.metadata['rotation']['angle'])

	@property
	def parity(self):
		return self.metadata['parity']['parity'] == 'pos'

	@property
	def pixel_scale(self):
		# unit is assumed to be arcseconds per pixel,
		# but can be found in self.metadata['pixel_scale']['unit']
		return float(self.metadata['pixel_scale']['scale'])

	def get_pixel_offset(self, reference_frame, average_pixel_scale_aspp):
		if reference_frame == self:
			return (0, 0)

		offset_x_deg = self.center[0] - reference_frame.center[0]
		offset_y_deg = self.center[1] - reference_frame.center[1]

		c = math.cos(math.radians(self.center[1]))

		offset_x_pix = -int(offset_x_deg * 3600.0 * c / average_pixel_scale_aspp)
		offset_y_pix = int(offset_y_deg * 3600.0 / average_pixel_scale_aspp)

		return (offset_x_pix, offset_y_pix)

	@staticmethod
	def get_astrometric_metadata(filepath, cpulimit=5):
		solve_command = [
			'/usr/local/astrometry/bin/solve-field',
			filepath,
			'--scale-units', 'arcsecperpix',
			'--scale-low', '0.8',
			'--scale-high', '1.0',
			'--cpulimit', str(cpulimit),
			'--overwrite',
			'--no-plots',
			'--parity', 'pos',
			'--temp-axy',
			'--solved', 'none',
			'--corr', 'none',
			'--new-fits', 'none',
			'--index-xyls', 'none',
			'--match', 'none',
			'--rdls', 'none',
			'--wcs', 'last_match.wcs',  # must be non-none so the detailed output is available
		]
		try:
			output = subprocess.check_output(solve_command, timeout=cpulimit, stderr=subprocess.DEVNULL).decode()
		except subprocess.TimeoutExpired:
			print('Timed out trying to solve field')
			return None

		# Output example:
		#
		# [...] pixel scale 0.907073 arcsec/pix.
		# [...]
		# Field center: (RA,Dec) = (114.133515, 65.594210) deg.
		# Field center: (RA H:M:S, Dec D:M:S) = (07:36:32.044, +65:35:39.156).
		# Field size: 28.9649 x 16.3092 arcminutes
		# Field rotation angle: up is 1.76056 degrees E of N
		# Field parity: pos
		# [...]

		metadata_regexes = {
			'pixel_scale': r'^.*pixel scale (?P<scale>[\d\.]*) (?P<unit>[\w\/]*)\..*$',
			'center_deg': r'^.*Field center: \(RA,Dec\) = \((?P<ra>[\d\.]*), (?P<dec>[\d\.]*)\) deg\..*$',
			'center': r'^.*Field center: \(RA H:M:S, Dec D:M:S\) = \((?P<ra>[\d\.\:]*), (?P<dec>[\d\.\:\+\-]*)\)\..*$',
			'size': r'^.*Field size: (?P<width>[\d\.]*) x (?P<height>[\d\.]*) (?P<unit>\w*).*$',
			'rotation': r'^.*Field rotation angle: up is (?P<angle>[\d\.]*) degrees (?P<direction>[WE]) of N.*$',
			'parity': r'^.*Field parity: (?P<parity>pos|neg).*$',
		}

		metadata = {}
		for metadata_key, metadata_regex in metadata_regexes.items():
			rx = re.compile(metadata_regex, re.DOTALL)
			match = rx.match(output)
			if not match:
				print('WARN: No match found for "{metadata_key}" in output of solve-field of file {filepath}.')
				print('Field may not have been solved or the output of the solver could not be parsed.')
			metadata[metadata_key] = match.groupdict() if match else None

		return metadata