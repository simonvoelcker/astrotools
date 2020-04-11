import math
import os
import re
import subprocess


class Frame:

	def __init__(self, filepath, metadata=None):
		self.filepath = filepath
		self.metadata = metadata

		self._pixel_offset = None
		self._angle = None

	@property
	def center(self):
		center_deg = self.metadata['center_deg']
		return float(center_deg['ra']), float(center_deg['dec'])

	@property
	def angle(self):
		return self._angle or float(self.metadata['rotation']['angle'])

	@property
	def parity(self):
		return self.metadata['parity']['parity'] == 'pos'

	@property
	def pixel_scale(self):
		# unit is assumed to be arcseconds per pixel,
		# but can be found in self.metadata['pixel_scale']['unit']
		return float(self.metadata['pixel_scale']['scale'])

	@property
	def pixel_offset(self):
		return self._pixel_offset

	def set_pixel_offset(self, pixel_offset):
		self._pixel_offset = pixel_offset

	def set_angle(self, angle):
		self._angle = angle

	def to_pixels(self, point_deg, pixel_scale_aspp):
		ra_aspp = pixel_scale_aspp / math.cos(math.radians(self.center[1]))
		dec_aspp = pixel_scale_aspp
		x_px = -point_deg[0] * 3600.0 / ra_aspp
		y_px =  point_deg[1] * 3600.0 / dec_aspp
		return (x_px, y_px)

	def get_offset_degrees(self, reference_frame):
		if reference_frame == self:
			return (0, 0)

		offset_x_deg = self.center[0] - reference_frame.center[0]
		offset_y_deg = self.center[1] - reference_frame.center[1]
		return (offset_x_deg, offset_y_deg)

	def get_pixel_offset(self, reference_frame, pixel_scale_aspp):
		offset_deg = (self.center[0] - reference_frame.center[0],
					  self.center[1] - reference_frame.center[1])
		return self.to_pixels(offset_deg, pixel_scale_aspp)

	def compute_astrometric_metadata(self, hint):
		return self.get_astrometric_metadata(self.filepath, hint=hint)

	@staticmethod
	def get_astrometric_metadata(filepath, cpulimit=5, hint=None):
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
		if hint is not None:
			solve_command += [
				'--ra', str(hint['ra']),
				'--dec', str(hint['dec']),
				'--radius', str(hint['radius']),
			]
		try:
			output = subprocess.check_output(solve_command, timeout=30, stderr=subprocess.DEVNULL).decode()
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
			'rotation': r'^.*Field rotation angle: up is (?P<angle>[\-\d\.]*) degrees (?P<direction>[WE]) of N.*$',
			'parity': r'^.*Field parity: (?P<parity>pos|neg).*$',
		}

		metadata = {}
		for metadata_key, metadata_regex in metadata_regexes.items():
			rx = re.compile(metadata_regex, re.DOTALL)
			match = rx.match(output)
			if not match:
				print(output)
				print(f'WARN: No match found for "{metadata_key}" in output of solve-field of file {filepath}.')
				print('Field may not have been solved or the output of the solver could not be parsed.')
				return None
			metadata[metadata_key] = match.groupdict() if match else None

		return metadata

	@classmethod
	def compute_frame_offsets(cls, frames, custom_offset=None):
		# average pixel scale
		pixel_scales = [frame.pixel_scale for frame in frames]
		average_pixel_scale_aspp = sum(pixel_scales) / len(pixel_scales)

		if custom_offset is not None:
			custom_x, custom_y = custom_offset.split(',')
			custom_x, custom_y = float(custom_x), float(custom_y)
		else:
			custom_x, custom_y = 0, 0

		# compute pixel offsets to reference frame
		reference_frame = frames[0]
		for frame_index, frame in enumerate(frames):  
			offset = frame.get_pixel_offset(reference_frame, average_pixel_scale_aspp)

			# apply additional custom offset if given
			offset = (offset[0] + custom_x * float(frame_index)/float(len(frames)-1),
					  offset[1] + custom_y * float(frame_index)/float(len(frames)-1))

			frame.set_pixel_offset(offset)

		# subtract min offset to it is zero and we only need to care about max		
		min_offset_x = min(frame.pixel_offset[0] for frame in frames)
		min_offset_y = min(frame.pixel_offset[1] for frame in frames)
		for frame in frames:
			frame.set_pixel_offset((int(frame.pixel_offset[0]-min_offset_x),
				                    int(frame.pixel_offset[1]-min_offset_y)))

	@classmethod
	def interpolate_angles(self, frames):
		# pretty cheap but it works for now
		first, last = frames[0].angle, frames[-1].angle
		for frame_index, frame in enumerate(frames):
			frame.set_angle(first + (last-first) * frame_index / (len(frames)-1))
