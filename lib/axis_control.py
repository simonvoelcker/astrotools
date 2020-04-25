import math
import re
import serial
import time


class AxisControl:
	control_response_rx = re.compile(r'\s*M(?P<motor>[12])\s+S=(?P<speed>-?\d+\.\d+)\s+P1=(?P<P1>-?\d+)\s+P2=(?P<P2>-?\d+)\s*')

	ra_resting_speed = -0.004725
	dec_resting_speed = 0.000075

	max_axis_speed = 0.3

	ra_axis_ratio = 69.0 * 3.0 * 2.0  # 2.0 is magic
	dec_axis_ratio = 105.6 * 2.0  # 2.0 is magic

	dec_backlash_direction = None  # +1, -1, None
	dec_backlash_revolutions = 0.55		# /2? *2?

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

	def set_motor_speed(self, motor, speed, quiet=False):
		if self.serial is None:
			if not quiet:
				print(f'Setting motor {motor} speed to {speed:9.6f} U/s (DRYRUN)')
		else:
			if not quiet:
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

	def _calc_ra_maneuver(self, ra_from, ra_to, max_speed_dps):
		if not ra_from or not ra_to or ra_from == ra_to:
			return None

		ra_axis_speed = self.max_axis_speed
		if max_speed_dps is not None:
			max_speed_override = max_speed_dps / 360.0 * self.ra_axis_ratio
			ra_axis_speed = min(ra_axis_speed, max_speed_override)

		ra_revolutions = (ra_to-ra_from) / 360.0 * self.ra_axis_ratio
		duration = abs(ra_revolutions / ra_axis_speed)
		ra_axis_speed = math.copysign(ra_axis_speed, ra_revolutions) + self.ra_resting_speed

		return ra_axis_speed, duration
		
	def _calc_dec_maneuver(self, dec_from, dec_to, max_speed_dps):
		if not dec_from or not dec_to or dec_from == dec_to:
			return None

		dec_axis_speed = self.max_axis_speed
		if max_speed_dps is not None:
			max_speed_override = max_speed_dps / 360.0 * self.dec_axis_ratio
			dec_axis_speed = min(dec_axis_speed, max_speed_override)

		dec_revolutions = (dec_to-dec_from) / 360.0 * self.dec_axis_ratio
		if self.dec_backlash_direction is not None:
			if self.dec_backlash_direction > 0 and dec_revolutions > 0:
				dec_revolutions += self.dec_backlash_revolutions
			elif self.dec_backlash_direction < 0 and dec_revolutions < 0:
				dec_revolutions -= self.dec_backlash_revolutions

		duration = abs(dec_revolutions / dec_axis_speed)
		dec_axis_speed = math.copysign(dec_axis_speed, dec_revolutions)

		# beware: magic minus
		dec_axis_speed = -dec_axis_speed

		return dec_axis_speed, duration

	def steer(self, here, target, max_speed_dps=None):

		if abs(target.ra - here.ra) > 0.075:
			ra_maneuver = self._calc_ra_maneuver(here.ra, target.ra, max_speed_dps)
		else:
			print('Skipping RA maneuver, error is small')
			ra_maneuver = None

		if abs(target.dec - here.dec) > 0.075:
			dec_maneuver = self._calc_dec_maneuver(here.dec, target.dec, max_speed_dps)
		else:
			print('Skipping Dec maneuver, error is small')
			dec_maneuver = None

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
			self.set_motor_speed('B', self.dec_resting_speed)
			ra_speed, ra_time = ra_maneuver
			self.set_motor_speed('A', ra_speed)
			print(f'Waiting {ra_time:6.3f} seconds')
			time.sleep(ra_time)
			self.set_motor_speed('A', self.ra_resting_speed)
		elif dec_maneuver:
			self.set_motor_speed('A', self.ra_resting_speed)
			dec_speed, dec_time = dec_maneuver
			self.set_motor_speed('B', dec_speed)
			print(f'Waiting {dec_time:6.3f} seconds')
			time.sleep(dec_time)
			self.set_motor_speed('B', self.dec_resting_speed)
