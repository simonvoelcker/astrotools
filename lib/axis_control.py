import math
import re
import serial
import time
import glob


class AxisSpeeds:

	ra_axis_ratio = 69.0 * 3.0 * 2.0  # 2.0 is magic
	dec_axis_ratio = 105.6 * 2.0  # 2.0 is magic

	max_speed_dps = 0.3

	# siderial speed plus typical drifting speeds
	# TODO the drift should not be part of the theoretical resting speed
	# it should be the default offset applied when the frontend calls /rest
	ra_resting_speed = -15.0 / 3600.0 + 0.2 / 3600.0
	dec_resting_speed = 0.0 / 3600.0 + 0.5 / 3600.0

	def __init__(self, ra_dps: float, dec_dps: float, mode: str):
		self.ra_dps = ra_dps
		self.dec_dps = dec_dps
		self.mode = mode

	@classmethod
	def ra_dps_to_axis(cls, ra_dps):
		return ra_dps / 360.0 * cls.ra_axis_ratio

	@classmethod
	def dec_dps_to_axis(cls, dec_dps):
		return dec_dps / 360.0 * cls.dec_axis_ratio

	@staticmethod
	def stopped():
		return AxisSpeeds(0, 0, 'stopped')


class AxisControl:
	control_response_rx = re.compile(
		r'\s*M(?P<motor>[12])\s+S=(?P<speed>-?\d+\.\d+)\s+P1=(?P<P1>-?\d+)\s+P2=(?P<P2>-?\d+)\s*'
	)

	def __init__(self, on_speeds_change=None):
		self.serial = None
		self.speeds = AxisSpeeds.stopped()
		self.on_speeds_change = on_speeds_change

	def connect(self):
		devices = glob.glob('/dev/ttyUSB*')
		if not devices:
			print('No USB devices found')
			return
		for device in devices:
			try:
				self.serial = serial.Serial(device, 9600, timeout=2)
				# connection cannot be used immediately ...yes, i know.
				time.sleep(2)
				print(f'Connected to motor control ({device})')
				return
			except serial.serialutil.SerialException:
				print(f'Failed to connect to motor control ({device})')

	def disconnect(self):
		self.serial = None

	def connected(self):
		return self.serial is not None

	def set_resting(self):
		self.set_axis_speeds(ra_dps=AxisSpeeds.ra_resting_speed, dec_dps=AxisSpeeds.dec_resting_speed, mode='resting')

	def set_axis_speeds(self, ra_dps=None, dec_dps=None, mode=None):
		if self.serial is not None:
			if ra_dps is not None:
				shaft_speed_rps = AxisSpeeds.ra_dps_to_axis(ra_dps)
				msg = f'A{shaft_speed_rps:9.6f}'
				self.serial.write(msg.encode())
			if dec_dps is not None:
				shaft_speed_rps = AxisSpeeds.dec_dps_to_axis(dec_dps)
				msg = f'B{shaft_speed_rps:9.6f}'
				self.serial.write(msg.encode())

		if ra_dps is not None:
			self.speeds.ra_dps = ra_dps
		if dec_dps is not None:
			self.speeds.dec_dps = dec_dps

		self.speeds.mode = mode
		self.on_speeds_change(self.speeds)

	def read_position(self):
		# this is too slow right now. revive later. also, make it a command of sorts.
		# pair the response with a timestamp and RA/Dec coordinates.
		response = self.serial.readline().decode()
		match = self.control_response_rx.match(response)
		if not match:
			print('Failed to parse response from the motor control!')
			print(response)
		return match.group('P1'), match.group('P2')

	@staticmethod
	def _calc_maneuver(axis, from_deg, to_deg, max_speed_dps=None):
		"""
		Compute an axis maneuver consisting of speed and duration.
		Does not add default resting speed.
		"""
		speed_dps = AxisSpeeds.max_speed_dps
		if max_speed_dps is not None:
			speed_dps = min(speed_dps, max_speed_dps)

		if axis == 'ra':
			revolutions = AxisSpeeds.ra_dps_to_axis(to_deg-from_deg)
			shaft_speed = AxisSpeeds.ra_dps_to_axis(speed_dps)
		else:
			revolutions = AxisSpeeds.dec_dps_to_axis(to_deg-from_deg)
			shaft_speed = AxisSpeeds.dec_dps_to_axis(speed_dps)

		duration = abs(revolutions / shaft_speed)
		speed_dps = math.copysign(speed_dps, revolutions)
		return speed_dps, duration

	def steer(self, here, target, max_speed_dps=None):

		if abs(target.ra - here.ra) > 0.075:
			ra_maneuver = self._calc_maneuver('ra', here.ra, target.ra, max_speed_dps)
		else:
			print('Skipping RA maneuver, error is small')
			ra_maneuver = None

		if abs(target.dec - here.dec) > 0.075:
			dec_maneuver = self._calc_maneuver('dec', here.dec, target.dec, max_speed_dps)
			# TODO beware: magic minus!
			dec_maneuver = -dec_maneuver[0], dec_maneuver[1]
		else:
			print('Skipping Dec maneuver, error is small')
			dec_maneuver = None

		# TODO restore combined maneuvers

		# if ra_maneuver and dec_maneuver:
		# 	# combined maneuver
		# 	ra_speed_dps, ra_time = ra_maneuver
		# 	dec_speed_dps, dec_time = dec_maneuver
		# 	# slow down the quicker maneuver to match execution times
		# 	if ra_time > dec_time:
		# 		dec_speed_dps *= dec_time / ra_time
		# 	else:
		# 		ra_speed_dps *= ra_time / dec_time
		# 	common_time = max(ra_time, dec_time)
		# 	self.set_axis_speeds(ra_dps=ra_speed_dps, dec_dps=dec_speed_dps, mode='steering')
		# 	print(f'Waiting {common_time:6.3f} seconds')
		# 	time.sleep(common_time)
		# 	self.set_resting()

		if ra_maneuver:
			ra_speed_dps, ra_time = ra_maneuver
			ra_speed_dps += AxisSpeeds.ra_resting_speed
			self.set_axis_speeds(ra_dps=ra_speed_dps, dec_dps=AxisSpeeds.dec_resting_speed, mode='steering')
			print(f'Waiting {ra_time:6.3f} seconds')
			time.sleep(ra_time)

			if ra_speed_dps * AxisSpeeds.ra_resting_speed < 0:
				# move again resting speed direction
				self.set_axis_speeds(ra_dps=math.copysign(0.1, ra_speed_dps), mode='BL-fix')
				time.sleep(5.0)
				# move with resting speed direction (into backlash)
				self.set_axis_speeds(ra_dps=math.copysign(0.1, AxisSpeeds.ra_resting_speed), mode='BL-fix')
				time.sleep(5.0)

			self.set_resting()

		if dec_maneuver:
			dec_speed_dps, dec_time = dec_maneuver
			dec_speed_dps += AxisSpeeds.dec_resting_speed
			self.set_axis_speeds(ra_dps=AxisSpeeds.ra_resting_speed, dec_dps=dec_speed_dps, mode='steering')
			print(f'Waiting {dec_time:6.3f} seconds')
			time.sleep(dec_time)

			if dec_speed_dps * AxisSpeeds.dec_resting_speed < 0:
				# move again resting speed direction
				self.set_axis_speeds(dec_dps=math.copysign(0.1, dec_speed_dps), mode='BL-fix')
				time.sleep(5.0)
				# move with resting speed direction (into backlash)
				self.set_axis_speeds(dec_dps=math.copysign(0.1, AxisSpeeds.dec_resting_speed), mode='BL-fix')
				time.sleep(5.0)

			self.set_resting()
