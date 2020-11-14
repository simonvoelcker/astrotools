import threading
import subprocess
import re

from lib.coordinates import Coordinates


def run_command(command, timeout, result):
	try:
		result['output'] = subprocess.check_output(command, timeout=timeout, stderr=subprocess.DEVNULL).decode()
	except subprocess.TimeoutExpired:
		result['timeout'] = True


class CalibrationData:
	def __init__(self, pixel_scale, ra_deg, dec_deg, angle, direction, parity, **kwargs):
		self.pixel_scale = float(pixel_scale)
		self.center_deg = Coordinates(float(ra_deg), float(dec_deg))
		self.rotation_angle = float(angle)
		self.rotation_direction = direction
		self.parity = parity


class Solver:
	"""
	The timeout is used in 3 (!) different ways here, only one of which actually works.
	
	(1) solve-field accepts a "cputime" parameter. Not effective.
	(2) subprocess.check_output accepts a timeout. Not effective.
	(3) check_output runs in a thread which is killed. Very effective.
	"""
	SOLVE_BINARY = '/usr/local/astrometry/bin/solve-field'

	@staticmethod
	def get_common_parameters(timeout=60.0, scale_low=0.8, scale_high=1.0):
		return [
			'--scale-units', 'arcsecperpix',
			'--scale-low', str(scale_low),
			'--scale-high', str(scale_high),
			'--cpulimit', str(timeout),
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
			'--wcs', 'temp/last_match.wcs',  # must be non-none so the detailed output is available
		]

	@staticmethod
	def get_hint_parameters(hint):
		if hint is None:
			return []
		return [
			'--ra', str(hint['ra']),
			'--dec', str(hint['dec']),
			'--radius', str(hint['radius']),
		]

	def get_analyze_command(self, filepaths, timeout, hint=None):
		batch_arg = ['--batch'] if len(filepaths) > 1 else []
		return [self.SOLVE_BINARY] + filepaths + batch_arg + self.get_common_parameters(timeout) + self.get_hint_parameters(hint)

	@staticmethod
	def run_in_thread(command, timeout):
		result = dict()
		thread = threading.Thread(target=run_command, args=(command, timeout, result))
		thread.start()
		thread.join(timeout=timeout)
		if 'output' in result:
			return result['output']

		# TODO kill process?
		# or try: -C / --cancel <filename>: filename whose creation signals the process to stop

		print('Timed out trying to solve field')
		return None

	def analyze_image(self, filepath, timeout=10, hint=None):
		command = self.get_analyze_command([filepath], timeout, hint)

		try:
			output = subprocess.check_output(command, timeout=timeout, stderr=subprocess.DEVNULL).decode()
		except subprocess.TimeoutExpired:
			return None

		# output = self.run_in_thread(command, timeout)
		# if not output:
		# 	return None

		# Output example:
		#
		# [...] pixel scale 0.907073 arcsec/pix.
		# [...]
		# Field: toughstuff/s10212.tif
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
			'rotation': r'^.*Field rotation angle: up is (?P<angle>[\-\d\.]*) degrees (?P<direction>[WE]) of N.*$',
			'parity': r'^.*Field parity: (?P<parity>pos|neg).*$',
		}

		metadata = {}
		for metadata_key, metadata_regex in metadata_regexes.items():
			rx = re.compile(metadata_regex, re.DOTALL)
			match = rx.match(output)
			if not match:
				print(f'WARN: No match found for "{metadata_key}" in output of solve-field of file {filepath}.')
				print('Field may not have been solved or the output of the solver could not be parsed.')
				return None
			metadata[metadata_key] = match.groupdict() if match else None

		return metadata

	def locate_image(self, filepath, timeout=10, hint=None):
		metadata = self.analyze_image(filepath, timeout, hint)
		if metadata is None:
			return None
		ra = float(metadata['center_deg']['ra'])
		dec = float(metadata['center_deg']['dec'])
		return Coordinates(ra, dec)

	def analyze_images(self, filepaths, timeout=60, hint=None):	
		command = self.get_analyze_command(filepaths, timeout, hint)
		print(f'Command:\n{" ".join(command)}')
		output = self.run_in_thread(command, timeout)
		if not output:
			return None

		# Output example:
		#
		# [...] pixel scale 0.907073 arcsec/pix.
		# [...]
		# Field: touchstuff/s10212.tif
		# Field center: (RA,Dec) = (114.133515, 65.594210) deg.
		# Field center: (RA H:M:S, Dec D:M:S) = (07:36:32.044, +65:35:39.156).
		# Field size: 28.9649 x 16.3092 arcminutes
		# Field rotation angle: up is 1.76056 degrees E of N
		# Field parity: pos
		# [...]

		pixel_scale_rx = re.compile(r'pixel scale (?P<scale>[\d.]*) (?P<unit>[\w/]*)\.')
		pixel_scales = [match.group('scale') for match in pixel_scale_rx.finditer(output)]

		frame_data_rx = re.compile(
			r'Field: (?P<path>.*)\n'
			r'Field center: \(RA,Dec\) = \((?P<ra_deg>[\d.]*), (?P<dec_deg>[\d.]*)\) deg\.\n'
			r'Field center: \(RA H:M:S, Dec D:M:S\) = \((?P<ra>[\d.:]*), (?P<dec>[\d.:+\-]*)\)\.\n'
			r'Field size: (?P<width>[\d.]*) x (?P<height>[\d.]*) (?P<unit>\w*)\n'
			r'Field rotation angle: up is (?P<angle>[\-\d.]*) degrees (?P<direction>[WE]) of N\n'
			r'Field parity: (?P<parity>pos|neg)'
		)
		frame_datas = [match.groupdict() for match in frame_data_rx.finditer(output)]
		
		if len(pixel_scales) != len(frame_datas):
			print('WARN: solve-field output could not be parsed or does not make sense')
			return dict()

		return {
			frame_data['path']: CalibrationData(pixel_scale, **frame_data)
			for pixel_scale, frame_data in zip(pixel_scales, frame_datas)
		}
