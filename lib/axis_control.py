import math
import re
import serial
import time


class AxisSpeeds(dict):

	ra_axis_ratio = 69.0 * 3.0 * 2.0  # 2.0 is magic
	dec_axis_ratio = 105.6 * 2.0  # 2.0 is magic

	max_axis_speed = 0.3

	ra_resting_speed = -0.004725
	dec_resting_speed = 0.000075

	def __init__(self, ra_revs_per_sec, dec_revs_per_sec):
		# inherit from dict to make this object json serializable on the cheap
		super().__init__(ra_revs_per_sec=ra_revs_per_sec, dec_revs_per_sec=dec_revs_per_sec)
		# these are MOTOR SHAFT revolutions per second
		self.ra_revs_per_sec = ra_revs_per_sec
		self.dec_revs_per_sec = dec_revs_per_sec

	@classmethod
	def ra_axis_to_dps(cls, ra_axis_speed):
		return ra_axis_speed / cls.ra_axis_ratio * 360.0

	@classmethod
	def dec_axis_to_dps(cls, dec_axis_speed):
		return dec_axis_speed / cls.dec_axis_ratio * 360.0

	@classmethod
	def ra_dps_to_axis(cls, ra_dps):
		return ra_dps / 360.0 * cls.ra_axis_ratio

	@classmethod
	def dec_dps_to_axis(cls, dec_dps):
		return dec_dps / 360.0 * cls.dec_axis_ratio

	@staticmethod
	def from_shaft_revolutions_per_second(ra, dec):
		return AxisSpeeds(ra, dec)

	@staticmethod
	def stopped():
		return AxisSpeeds(0, 0)

	@classmethod
	def resting_speeds(cls):
		return AxisSpeeds(cls.ra_resting_speed, cls.dec_resting_speed)


class AxisControl:
	control_response_rx = re.compile(r'\s*M(?P<motor>[12])\s+S=(?P<speed>-?\d+\.\d+)\s+P1=(?P<P1>-?\d+)\s+P2=(?P<P2>-?\d+)\s*')

	dec_backlash_direction = None  # +1, -1, None
	dec_backlash_revolutions = 0.55		# /2? *2?

	def __init__(self, on_speeds_change=None):
		self.serial = None
		self.speeds = AxisSpeeds.stopped()
		self.on_speeds_change = on_speeds_change

	def get_speeds(self):
		# TODO must get used to DPS at some point
		return {
			'ra': self.speeds.ra_revs_per_sec,
			'dec': self.speeds.dec_revs_per_sec,
			'ra_dps': AxisSpeeds.ra_axis_to_dps(self.speeds.ra_revs_per_sec),
			'dec_dps': AxisSpeeds.dec_axis_to_dps(self.speeds.dec_revs_per_sec),
		}

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

	def set_motor_speed(self, axis, axis_speed):
		if self.serial is not None:
			motor_key = 'A' if axis == 'ra' else 'B'
			msg = f'{motor_key}{axis_speed:9.6f}'
			self.serial.write(msg.encode())

		if axis == 'ra':
			self.speeds.ra_revs_per_sec = axis_speed
		else:
			self.speeds.dec_revs_per_sec = axis_speed

		if axis == 'dec':
			self.dec_backlash_direction = 1 if axis_speed > 0 else -1

		self.on_speeds_change(self.speeds)

	def read_position(self):
		# this is too slow right now. revive later.
		response = self.serial.readline().decode()
		match = self.control_response_rx.match(response)
		if not match:
			print('Failed to parse response from the motor control!')
			print(response)
		return match.group('P1'), match.group('P2')

	@staticmethod
	def _calc_ra_maneuver(ra_from, ra_to, max_speed_dps):
		if not ra_from or not ra_to or ra_from == ra_to:
			return None

		ra_axis_speed = AxisSpeeds.max_axis_speed
		if max_speed_dps is not None:
			max_speed_override = AxisSpeeds.ra_dps_to_axis(max_speed_dps)
			ra_axis_speed = min(ra_axis_speed, max_speed_override)

		ra_revolutions = AxisSpeeds.ra_dps_to_axis(ra_to-ra_from)
		duration = abs(ra_revolutions / ra_axis_speed)
		ra_axis_speed = math.copysign(ra_axis_speed, ra_revolutions) + AxisSpeeds.ra_resting_speed

		return ra_axis_speed, duration
		
	def _calc_dec_maneuver(self, dec_from, dec_to, max_speed_dps):
		if not dec_from or not dec_to or dec_from == dec_to:
			return None

		dec_axis_speed = AxisSpeeds.max_axis_speed
		if max_speed_dps is not None:
			max_speed_override = AxisSpeeds.dec_dps_to_axis(max_speed_dps)
			dec_axis_speed = min(dec_axis_speed, max_speed_override)

		dec_revolutions = AxisSpeeds.dec_dps_to_axis(dec_to-dec_from)
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
			self.set_motor_speed('ra', ra_speed)
			self.set_motor_speed('dec', dec_speed)
			print(f'Waiting {common_time:6.3f} seconds')
			time.sleep(common_time)
			self.set_motor_speed('ra', AxisSpeeds.ra_resting_speed)
			self.set_motor_speed('dec', AxisSpeeds.dec_resting_speed)
		elif ra_maneuver:
			self.set_motor_speed('dec', AxisSpeeds.dec_resting_speed)
			ra_speed, ra_time = ra_maneuver
			self.set_motor_speed('ra', ra_speed)
			print(f'Waiting {ra_time:6.3f} seconds')
			time.sleep(ra_time)
			self.set_motor_speed('ra', AxisSpeeds.ra_resting_speed)
		elif dec_maneuver:
			self.set_motor_speed('ra', AxisSpeeds.ra_resting_speed)
			dec_speed, dec_time = dec_maneuver
			self.set_motor_speed('dec', dec_speed)
			print(f'Waiting {dec_time:6.3f} seconds')
			time.sleep(dec_time)
			self.set_motor_speed('dec', AxisSpeeds.dec_resting_speed)
