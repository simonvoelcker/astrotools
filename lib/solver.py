import threading
import time
import subprocess
import re

from lib.coordinates import Coordinates


def run_command(command, timeout, result):
	try:
		result['output'] = subprocess.check_output(command, timeout=timeout, stderr=subprocess.DEVNULL).decode()
	except subprocess.TimeoutExpired:
		result['timeout'] = True


class Solver:
	"""
	The timeout is used in 3 (!) different ways here, only one of which actually works.
	
	(1) solve-field accepts a "cputime" parameter. Not effective.
	(2) subprocess.check_output accepts a timeout. Not effective.
	(3) check_output runs in a thread which is killed. Very effective.
	"""
	def __init__(self):
		super().__init__()

	def get_locate_command(self, filepath, timeout):
		return [
			'/usr/local/astrometry/bin/solve-field',
			filepath,
			'--scale-units', 'arcsecperpix',
			'--scale-low', '0.8',
			'--scale-high', '1.0',
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
			'--wcs', 'none',
		]

	def get_analyze_command(self, filepath, timeout, hint):
		solve_command = [
			'/usr/local/astrometry/bin/solve-field',
			filepath,
			'--scale-units', 'arcsecperpix',
			'--scale-low', '0.8',
			'--scale-high', '1.0',
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
			'--wcs', 'last_match.wcs',  # must be non-none so the detailed output is available
		]
		if hint is not None:
			solve_command += [
				'--ra', str(hint['ra']),
				'--dec', str(hint['dec']),
				'--radius', str(hint['radius']),
			]
		return solve_command

	def run_in_thread(self, command, timeout):
		result = dict()
		thread = threading.Thread(target=run_command, args=(command, timeout, result))
		thread.start()
		thread.join(timeout=timeout)
		if 'output' in result:
			return result['output']

		print('Timed out trying to solve field')
		return None

	def analyze_image(self, filepath, timeout=10, hint=None):
		command = self.get_analyze_command(filepath, timeout, hint)
		output = self.run_in_thread(command, timeout)
		if not output:
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
				print(f'WARN: No match found for "{metadata_key}" in output of solve-field of file {filepath}.')
				print('Field may not have been solved or the output of the solver could not be parsed.')
				return None
			metadata[metadata_key] = match.groupdict() if match else None

		return metadata

	def locate_image(self, filepath, timeout=10):
		command = self.get_locate_command(filepath, timeout)
		output = self.run_in_thread(command, timeout)
		if not output:
			return None

		astrometry_coordinates_rx = re.compile(r'^.*RA,Dec = \((?P<ra>[\d\.]+),(?P<dec>[\d\.]+)\).*$', re.DOTALL)
		match = astrometry_coordinates_rx.match(output)
		if not match:
			return None
		return Coordinates(float(match.group('ra')), float(match.group('dec')))
