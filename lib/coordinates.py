import re


class Coordinates:
	# format that's easy to type on the command line
	# TODO make the seconds/arcseconds part optional
	string_format_rx = re.compile(r'(?P<ra>.+):(?P<dec>.+)')
	ra_string_format_rx = re.compile(r'(?P<h>\d+)h(?P<m>\d+)m(?P<s>\d+)s')
	dec_string_format_rx = re.compile(r'(?P<sign>[\+\-]?)(?P<d>\d+)d(?P<m>\d+)m(?P<s>\d+)s')
	# format found in the catalog CSV file 
	csv_ra_format_rx = re.compile(r'(?P<h>\d+):(?P<m>\d+):(?P<s>[\d\.]+)')
	csv_dec_format_rx = re.compile(r'(?P<sign>[\+\-]?)(?P<d>\d+):(?P<m>\d+):(?P<s>[\d\.]+)')

	def __init__(self, ra, dec):
		# the canonical representation of RA and DEC shall be in degrees, as float
		self.ra = ra
		self.dec = dec

	def __str__(self):
		return f'(RA={self.ra:6.3f}, DEC={self.dec:6.3f})'	

	@classmethod
	def parse_csvformat(cls, ra_str, dec_str):
		# format is 12:45:32.0 for both RA/DEC
		ra_match = cls.csv_ra_format_rx.match(ra_str)
		dec_match = cls.csv_dec_format_rx.match(dec_str)
		return Coordinates.from_matches(ra_match, dec_match)

	@classmethod
	def parse(cls, coordinates_string):
		# parse coordinates from my own ghetto format: __h__m__s:__d__m__s
		coordinates_match = cls.string_format_rx.match(coordinates_string)
		if coordinates_match is None:
			print(f'Failed to parse coordinates: {coordinates_string}')
			return None

		ra_str = coordinates_match.group('ra')
		dec_str = coordinates_match.group('dec')

		ra_match = cls.ra_string_format_rx.match(ra_str)
		dec_match = cls.dec_string_format_rx.match(dec_str)
		return Coordinates.from_matches(ra_match, dec_match)

	@classmethod
	def from_matches(cls, ra_match, dec_match):
		if ra_match is None:
			print(f'Failed to parse right ascension')
			return None
		hours = int(ra_match.group('h'))
		minutes = int(ra_match.group('m'))
		seconds = float(ra_match.group('s'))
		# convert to hours (float), then on to degrees (15 degrees to the hour)
		ra_hours = hours + minutes / 60.0 + seconds / 3600.0	
		ra_degrees = 15.0 * ra_hours

		if dec_match is None:
			print(f'Failed to parse declination')
			return None
		degrees = int(dec_match.group('d'))
		arcmin = int(dec_match.group('m'))
		arcsec = float(dec_match.group('s'))
		sign = -1 if dec_match.group('sign') == '-' else 1
		# convert to degrees (float)
		dec_degrees = sign * (float(degrees) + arcmin / 60.0 + arcsec / 3600.0)

		return Coordinates(ra_degrees, dec_degrees)

	def format(self):
		# format coordinates from angles to my ghetto format: __h__m__s:__d__m__s
		ra_degrees_f = self.ra
		dec_degrees_f = self.dec
		
		ra_hours_f = ra_degrees_f / 15.0
		ra_hours = int(ra_hours_f)
		ra_hours_remain = ra_hours_f - ra_hours
		ra_minutes_f = 60.0 * ra_hours_remain
		ra_minutes = int(ra_minutes_f)
		ra_minutes_remain = ra_minutes_f - ra_minutes
		ra_seconds_f = 60.0 * ra_minutes_remain
		ra_seconds = int(ra_seconds_f)

		dec_sign = '-' if dec_degrees_f < 0 else '+'
		dec_degrees_f = abs(dec_degrees_f)
		dec_degrees = int(dec_degrees_f)
		dec_degrees_remain = dec_degrees_f - dec_degrees
		dec_moa_f = 60.0 * dec_degrees_remain
		dec_moa = int(dec_moa_f)
		dec_moa_remain = dec_moa_f - dec_moa
		dec_soa_f = 60.0 * dec_moa_remain
		dec_soa = int(dec_soa_f)

		return f'{ra_hours:2}h{ra_minutes:2}m{ra_seconds:2}s:{dec_sign}{dec_degrees}d{dec_moa:2}m{dec_soa:2}s'

