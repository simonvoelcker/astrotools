import re
import sys
import serial
import argparse
import time


class AxisControl:
	control_response_rx = re.compile(r'\s*M(?P<motor>[12])\s+S=(?P<speed>\-?\d+\.\d+)\s+P1=(?P<P1>\-?\d+)\s+P2=(?P<P2>\-?\d+)\s*')

	ra_resting_speed = -0.0047
	dec_resting_speed = 0.0

	ra_max_speed = 0.4
	dec_max_speed = 0.3

	ra_axis_ratio = 69.0 * 3.0 * 2.0  # 2.0 is magic
	dec_axis_ratio = 105.6 * 2.0  # 2.0 is magic

	def __init__(self, usb_ports=None):
		self.serial = None

		if usb_ports is None:
			return  # dryrun mode

		for port in usb_ports:
			try:
				self.serial = serial.Serial(f'/dev/ttyUSB{port}', 9600, timeout=2)
				# connection cannot be used immediately ...yes, i know.
				time.sleep(2)
				print(f'Connected to motor control on port {port}.')
				return
			except serial.serialutil.SerialException:
				print(f'Failed to connect to motor control on port {port}.')

	def set_motor_speed(self, motor, speed):
		if self.serial is None:
			print(f'Would set motor {motor} speed to {speed} U/s')
		else:
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
			return None
		ra_str = coordinates_match.group('ra')
		if ra_str:
			ra_match = ra_rx.match(ra_str)
			if ra_match is None:
				print(f'Failed to parse right ascension: {ra_str}')
				return None
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
				return None
			degrees = int(dec_match.group('d'))
			arcmin = int(dec_match.group('m'))
			arcsec = int(dec_match.group('s'))
			# convert to degrees (float)
			dec_degrees = float(degrees) + arcmin / 60.0 + arcsec / 3600.0
		else:
			dec_degrees = None

		return ra_degrees, dec_degrees

	def steer(self, here_coordinates, target_coordinates):
		print('Setting motors to resting speed')
		self.set_motor_speed('A', self.ra_resting_speed)
		self.set_motor_speed('B', self.dec_resting_speed)

		ra_from, dec_from = here_coordinates
		ra_to, dec_to = target_coordinates

		if ra_from and ra_to:
			ra_revolutions = (ra_to-ra_from) / 360.0 * self.ra_axis_ratio
			ra_speed = (self.ra_max_speed if ra_revolutions > 0 else -self.ra_max_speed) + self.ra_resting_speed
			ra_time = abs(ra_revolutions / ra_speed)

			if ra_revolutions > 0 and ra_time < 5:
				# just wait at zero speed instead of steering
				ra_speed = 0
				ra_time = ra_revolutions / -self.ra_resting_speed
			
			print(f'Setting RA axis speed to {ra_speed} for {ra_time} seconds, then back to resting speed')
			self.set_motor_speed('A', ra_speed)
			time.sleep(ra_time)
			self.set_motor_speed('A', self.ra_resting_speed)

		if dec_from and dec_to:
			dec_revolutions = (dec_to-dec_from) / 360.0 * self.dec_axis_ratio
			dec_speed = -self.dec_max_speed if dec_revolutions > 0 else self.dec_max_speed
			dec_time = abs(dec_revolutions / dec_speed)

			print(f'Setting DEC axis speed to {dec_speed} for {dec_time} seconds, then back to resting speed')
			self.set_motor_speed('B', dec_speed)
			time.sleep(dec_time)
			self.set_motor_speed('B', self.dec_resting_speed)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--here', type=str, help='Current position. Format: __h__m__s:__d__m__s')
	parser.add_argument('--target', type=str, help='Target position. Format: __h__m__s:__d__m__s')
	parser.add_argument('--usb-port', type=int, default=None, help='USB port to use for the motor control. Omit for no motor control.')
	args = parser.parse_args()

	here_coordinates = AxisControl.parse_coordinates(args.here)
	target_coordinates = AxisControl.parse_coordinates(args.target)

	axis_control = AxisControl([args.usb_port, 1-args.usb_port] if args.usb_port is not None else None)
	axis_control.steer(here_coordinates, target_coordinates)
