import re
from dataclasses import dataclass
from typing import Union

from lib.config import (
	SOLVE_BINARY,
	SOLVE_PIXEL_SCALE_HIGH,
	SOLVE_PIXEL_SCALE_LOW,
)
from lib.coordinates import Coordinates
from lib.util import run_command_or_die_trying


@dataclass
class CalibrationData:
	pixel_scale: float
	pixel_scale_unit: str  # "arcsecpix" or so
	center_deg: Coordinates
	rotation_angle: float
	rotation_direction: str  # "E of N"/"W of N"
	parity: str  # "pos"/"neg"

	def to_dict(self):
		return {
			k: v.to_dict() if hasattr(v, 'to_dict') else v
			for k, v in self.__dict__.items()
		}


class Solver:
	"""
	The timeout is used in 3 (!) different ways here, only one of which actually works.
	
	(1) solve-field accepts a "cputime" parameter. Not effective.
	(2) subprocess.check_output accepts a timeout. Not effective.
	(3) check_output runs in a thread which is killed. Very effective.
	"""
	@staticmethod
	def get_common_parameters(
		timeout=60.0,
		scale_low=SOLVE_PIXEL_SCALE_LOW,
		scale_high=SOLVE_PIXEL_SCALE_HIGH,
	):
		return [
			'--scale-units', 'arcsecperpix',
			'--scale-low', str(scale_low),
			'--scale-high', str(scale_high),
			'--cpulimit', str(timeout),
			'--overwrite',
			'--no-plots',
			'--temp-axy',
			'--solved', 'none',
			'--corr', 'none',
			'--new-fits', 'none',
			'--index-xyls', 'none',
			'--match', 'none',
			'--rdls', 'none',
			'--wcs', 'temp/last_match.wcs',  # must be non-none so the detailed output is available
		]

	def get_analyze_command(self, filepaths, timeout):
		return [SOLVE_BINARY] + filepaths + self.get_common_parameters(timeout)

	def analyze_image(self, filepath, timeout=30, run_callback=None) -> Union[CalibrationData, None]:
		command = self.get_analyze_command([filepath], timeout)
		output = run_command_or_die_trying(command, timeout, run_callback)
		if output is None:
			return None

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

		output_regexes = {
			'pixel_scale': r'^.*pixel scale (?P<scale>[\d\.]*) (?P<unit>[\w\/]*)\..*$',
			'center_deg': r'^.*Field center: \(RA,Dec\) = \((?P<ra>[\d\.]*), (?P<dec>[\-\d\.]*)\) deg\..*$',
			'center': r'^.*Field center: \(RA H:M:S, Dec D:M:S\) = \((?P<ra>[\d\.\:]*), (?P<dec>[\d\.\:\+\-]*)\)\..*$',
			'size': r'^.*Field size: (?P<width>[\d\.]*) x (?P<height>[\d\.]*) (?P<unit>\w*).*$',
			'rotation': r'^.*Field rotation angle: up is (?P<angle>[\-\d\.]*) degrees (?P<direction>[WE]) of N.*$',
			'parity': r'^.*Field parity: (?P<parity>pos|neg).*$',
		}

		parsed_data = {}
		for output_key, output_regex in output_regexes.items():
			rx = re.compile(output_regex, re.DOTALL)
			match = rx.match(output)
			if not match:
				print(f'WARN: No match found for "{output_key}" in output of solve-field of file {filepath}.')
				print(f'Field may not have been solved or the output of the solver could not be parsed. Full output:\n{output}')
				return None
			parsed_data[output_key] = match.groupdict()

		return CalibrationData(
			pixel_scale=float(parsed_data['pixel_scale']['scale']),
			pixel_scale_unit=str(parsed_data['pixel_scale']['unit']),
			center_deg=Coordinates(
				float(parsed_data['center_deg']['ra']),
				float(parsed_data['center_deg']['dec'])
			),
			rotation_angle=float(parsed_data['rotation']['angle']),
			rotation_direction=str(parsed_data['rotation']['direction']),
			parity=str(parsed_data['parity']['parity']),
		)
