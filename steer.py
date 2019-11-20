import re
import sys
import serial
import argparse
import time


class AxisControl:
	control_response_rx = re.compile(r'\s*M(?P<motor>[12])\s+S=(?P<speed>\-?\d+\.\d+)\s+P1=(?P<P1>\-?\d+)\s+P2=(?P<P2>\-?\d+)\s*')

	def __init__(self, usb_ports):
		for port in usb_ports:
			try:
				self.serial = serial.Serial(f'/dev/ttyUSB{port}', 9600, timeout=2)
				# connection cannot be used immediately ...yes, i know.
				time.sleep(2)
				print(f'Connected to motor control on port {port}.')
				return
			except serial.serialutil.SerialException:
				print(f'Failed to connect to motor control on port {port}.')
		sys.exit(1)

	def set_motor_speed(self, motor, speed):
		msg = f'{motor}{speed:9.6f}'
		self.serial.write(msg.encode())

	def read_position(self):
		# this is too slow right now. revive later.
		response = self.serial.readline().decode()
		match = self.control_response_rx.match(response)
		if not match:
			print('Failed to parse response from the motor control!')
			print(response)
		return match.group('P1'), match.group('P2')

	@staticmethod
	def parse_coordinates(coordinates):
		# parse coordinates from format: __h__m__s:__d__m__s, convert to angles (arcsecs)
		# coordinates may be omitted, but the separating colon is mandatory
		#
		# no support for negative declination
		# 
		coordinates_rx = re.compile(r'(?P<ra>.*)?:(?P<dec>.*)?')
		ra_rx = re.compile(r'(?P<h>\d+)h(?P<m>\d+)m(?P<s>\d+)s')
		dec_rx = re.compile(r'(?P<d>\d+)d(?P<m>\d+)m(?P<s>\d+)s')

		coordinates_match = coordinates_rx.match(coordinates)
		if coordinates_match is None:
			print(f'Failed to parse coordinates: {coordinates}')
			sys.exit()
		ra_str = coordinates_match.group('ra')
		if ra_str:
			ra_match = ra_rx.match(ra_str)
			if ra_match is None:
				print(f'Failed to parse right ascension: {ra_str}')
				sys.exit()
			hours = int(ra_match.group('h'))
			arcmin = int(ra_match.group('m'))
			arcsec = int(ra_match.group('s'))
			# convert to hours (float), then on to degrees (15 degrees to the hour)
			ra_hours = hours + arcmin / 60.0 + arcsec / 3600.0	
			ra_degrees = 15.0 * ra_hours
		else:
			ra_degrees = None

		dec_str = coordinates_match.group('dec')
		if dec_str:
			dec_match = dec_rx.match(dec_str)
			if dec_match is None:
				print(f'Failed to parse declination: {dec_str}')
				sys.exit()
			degrees = int(dec_match.group('d'))
			arcmin = int(dec_match.group('m'))
			arcsec = int(dec_match.group('s'))
			# convert to degrees (float)
			dec_degrees = float(degrees) + arcmin / 60.0 + arcsec / 3600.0
		else:
			dec_degrees = None

		return ra_degrees, dec_degrees


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--here', type=str, help='Current position. Format: __h__m__s:__d__m__s')
	parser.add_argument('--target', type=str, help='Target position. Format: __h__m__s:__d__m__s')
	args = parser.parse_args()

	ra_from, dec_from = AxisControl.parse_coordinates(args.here)
	ra_to, dec_to = AxisControl.parse_coordinates(args.target)

	ra_resting_speed = -0.0048
	dec_resting_speed = 0.0

	ra_max_speed = 0.5
	dec_max_speed = 0.01

	# 2.0 is magic
	ra_axis_ratio = 207.0 * 2.0
	dec_axis_ratio = 69.0 * 2.0

	if ra_from and ra_to:
		ra_revolutions = (ra_to-ra_from) / 360.0 * ra_axis_ratio
		ra_speed = ra_max_speed if ra_revolutions > 0 else -ra_max_speed
		ra_time = abs(ra_revolutions / ra_speed)
		print(f'Should set RA axis speed to {ra_speed} for {ra_time} seconds')

		if ra_revolutions > 0:
			ra_rest_time = ra_revolutions / -ra_resting_speed
			print(f'Alternative: set RA speed to 0 for {ra_rest_time} seconds')

	if dec_from and dec_to:
		dec_revolutions = (dec_to-dec_from) / 360.0 * dec_axis_ratio
		dec_speed = -dec_max_speed if dec_revolutions > 0 else dec_max_speed
		dec_time = abs(dec_revolutions / dec_speed)
		print(f'Should set DEC axis speed to {dec_speed} for {dec_time} seconds')
