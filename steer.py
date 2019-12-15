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

	dec_backlash_direction = None  # +1, -1, None
	dec_backlash_revolutions = 0.2

	def __init__(self):
		self.serial = None

	def connect(self, usb_ports):
		for port in usb_ports:
			try:
				self.serial = serial.Serial(f'/dev/ttyUSB{port}', 9600, timeout=2)
				# connection cannot be used immediately ...yes, i know.
				time.sleep(2)
				print(f'Connected to motor control on port {port}.')
				return
			except serial.serialutil.SerialException:
				print(f'Failed to connect to motor control on port {port}.')

	def disconnect(self):
		self.serial = None

	def connected(self):
		return self.serial is not None

	def set_motor_speed(self, motor, speed):
		if self.serial is None:
			print(f'Setting motor {motor} speed to {speed:9.6f} U/s (DRYRUN)')
		else:
			print(f'Setting motor {motor} speed to {speed:9.6f} U/s')
			msg = f'{motor}{speed:9.6f}'
			self.serial.write(msg.encode())
		if motor == 'B':
			self.dec_backlash_direction = 1 if speed > 0 else -1

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

		coordinates_rx = re.compile(r'(?P<ra>.*)?:(?P<dec>.*)?')
		ra_rx = re.compile(r'(?P<h>\d+)h(?P<m>\d+)m(?P<s>\d+)s')
		dec_rx = re.compile(r'(?P<sign>[\+\-]?)(?P<d>\d+)d(?P<m>\d+)m(?P<s>\d+)s')

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
			sign = -1 if dec_match.group('sign') == '-' else 1
			# convert to degrees (float)
			dec_degrees = sign * (float(degrees) + arcmin / 60.0 + arcsec / 3600.0)
		else:
			dec_degrees = None

		return ra_degrees, dec_degrees

	@staticmethod
	def format_coordinates(coordinates):
		# format coordinates from angles to __h__m__s:__d__m__s
		ra_degrees_f, dec_degrees_f = coordinates
		
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

	def _calc_ra_maneuver(self, ra_from, ra_to):
		if not ra_from or not ra_to or ra_from == ra_to:
			return None

		ra_revolutions = (ra_to-ra_from) / 360.0 * self.ra_axis_ratio
		ra_speed = (self.ra_max_speed if ra_revolutions > 0 else -self.ra_max_speed) + self.ra_resting_speed
		ra_time = abs(ra_revolutions / ra_speed)

		if ra_revolutions > 0 and ra_time < 5:
			# just wait at zero speed instead of steering
			ra_speed = 0
			ra_time = ra_revolutions / -self.ra_resting_speed

		return ra_speed, ra_time
		
	def _calc_dec_maneuver(self, dec_from, dec_to):
		if not dec_from or not dec_to or dec_from == dec_to:
			return None

		dec_revolutions = (dec_to-dec_from) / 360.0 * self.dec_axis_ratio

		if self.dec_backlash_direction is not None:
			if self.dec_backlash_direction > 0 and dec_revolutions > 0:
				print(f'Applying backlash correction due to direction change: {dec_revolutions} revs => {dec_revolutions + self.dec_backlash_revolutions} revs')
				dec_revolutions += self.dec_backlash_revolutions
			elif self.dec_backlash_direction < 0 and dec_revolutions < 0:
				print(f'Applying backlash correction due to direction change: {dec_revolutions} revs => {dec_revolutions - self.dec_backlash_revolutions} revs')
				dec_revolutions -= self.dec_backlash_revolutions

		dec_speed = -self.dec_max_speed if dec_revolutions > 0 else self.dec_max_speed
		dec_time = abs(dec_revolutions / dec_speed)

		return dec_speed, dec_time

	def steer(self, here_coordinates, target_coordinates):
		ra_from, dec_from = here_coordinates
		ra_to, dec_to = target_coordinates

		ra_maneuver = self._calc_ra_maneuver(ra_from, ra_to)
		dec_maneuver = self._calc_dec_maneuver(dec_from, dec_to)

		if ra_maneuver and dec_maneuver:
			# combined maneuver
			ra_speed, ra_time = ra_maneuver
			dec_speed, dec_time = dec_maneuver
			# slow down the quicker maneuver to match execution times
			if ra_time > dec_time:
				dec_speed *= dec_time / ra_time
			else:
				ra_speed *= ra_time / dec_time
			common_time = max(ra_time, dec_time)
			self.set_motor_speed('A', ra_speed)
			self.set_motor_speed('B', dec_speed)
			print(f'Waiting {common_time:6.3f} seconds')
			time.sleep(common_time)
			self.set_motor_speed('A', self.ra_resting_speed)
			self.set_motor_speed('B', self.dec_resting_speed)
		elif ra_maneuver:
			ra_speed, ra_time = ra_maneuver
			self.set_motor_speed('A', ra_speed)
			print(f'Waiting {ra_time:6.3f} seconds')
			time.sleep(ra_time)
			self.set_motor_speed('A', self.ra_resting_speed)
		elif dec_maneuver:
			dec_speed, dec_time = dec_maneuver
			self.set_motor_speed('B', dec_speed)
			print(f'Waiting {dec_time:6.3f} seconds')
			time.sleep(dec_time)
			self.set_motor_speed('B', self.dec_resting_speed)
