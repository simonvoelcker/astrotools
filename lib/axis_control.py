import math
import re
import serial
import time
import glob

from dataclasses import dataclass

from lib.config import RA_AXIS_RATIO, DEC_AXIS_RATIO, MAX_AXIS_SPEED_DPS


class AxisSpeeds:
	# Theoretical resting speed assuming Siderial day
	# Unit is degrees per second, /3600 makes it arc-secs per second.
	ra_resting_speed = -15.0 / 3600.0
	dec_resting_speed = 0.0 / 3600.0

	def __init__(self, ra_dps: float, dec_dps: float, mode: str):
		self.ra_dps = ra_dps
		self.dec_dps = dec_dps
		self.mode = mode

	@classmethod
	def ra_dps_to_axis(cls, ra_dps):
		return ra_dps / 360.0 * RA_AXIS_RATIO

	@classmethod
	def dec_dps_to_axis(cls, dec_dps):
		return dec_dps / 360.0 * DEC_AXIS_RATIO

	@staticmethod
	def stopped():
		return AxisSpeeds(0, 0, 'stopped')


@dataclass
class Maneuver:
	ra_dps: float = 0.0
	dec_dps: float = 0.0
	mode: str = ''
	duration: float = 0.0


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
		ra_str = f'RA={ra_dps:9.6f} dps' if ra_dps else ''
		dec_str = f'Dec={dec_dps:9.6f} dps' if dec_dps else ''
		mode_str = f'Mode={mode}' if mode else ''
		print(f'Setting {ra_str} {dec_str} {mode_str}')

		if self.serial is not None:
			if ra_dps is not None:
				shaft_speed_rps = AxisSpeeds.ra_dps_to_axis(ra_dps)
				msg = f'set spd axis=r value={shaft_speed_rps:9.6f}'
				self.serial.write(msg.encode())
			if dec_dps is not None:
				shaft_speed_rps = AxisSpeeds.dec_dps_to_axis(dec_dps)
				msg = f'set spd axis=d value={shaft_speed_rps:9.6f}'
				self.serial.write(msg.encode())

		if ra_dps is not None:
			self.speeds.ra_dps = ra_dps
		if dec_dps is not None:
			self.speeds.dec_dps = dec_dps

		self.speeds.mode = mode

		if self.on_speeds_change is not None:
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
		speed_dps = MAX_AXIS_SPEED_DPS
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

	def get_steering_maneuvers(self, here, target, max_speed_dps=None):
		# force slow maneuver if close to target already
		max_distance_deg = max(abs(here.ra-target.ra), abs(here.dec-target.dec))
		if max_distance_deg < 1.0:
			max_speed_dps = 0.1

		ra_speed_dps, ra_time = self._calc_maneuver('ra', here.ra, target.ra, max_speed_dps)
		dec_speed_dps, dec_time = self._calc_maneuver('dec', here.dec, target.dec, max_speed_dps)

		# caution: magic minus!
		dec_speed_dps = -dec_speed_dps

		# slow down the quicker maneuver to match execution times
		if ra_time > dec_time:
			dec_speed_dps *= dec_time / ra_time
		else:
			ra_speed_dps *= ra_time / dec_time
		common_time = max(ra_time, dec_time)

		# superimpose maneuver with resting speeds
		ra_speed_dps += AxisSpeeds.ra_resting_speed
		dec_speed_dps += AxisSpeeds.dec_resting_speed

		mode = f'Steering ({int(common_time)}s)'
		yield Maneuver(ra_speed_dps, dec_speed_dps, mode, common_time)

		# apply backlash compensation if we moved against resting direction
		compensate_ra = bool(ra_speed_dps * AxisSpeeds.ra_resting_speed < 0)
		compensate_dec = bool(dec_speed_dps * AxisSpeeds.dec_resting_speed < 0)

		if compensate_ra or compensate_dec:
			dps = 0.1
			duration = 10.0
			# move further against backlash on those axes which also did so before
			ra_dps = math.copysign(dps, ra_speed_dps) if compensate_ra else AxisSpeeds.ra_resting_speed
			dec_dps = math.copysign(dps, dec_speed_dps) if compensate_dec else AxisSpeeds.dec_resting_speed
			yield Maneuver(ra_dps, dec_dps, 'BL-compensation', duration)

			# move back into backlash
			ra_dps = math.copysign(dps, AxisSpeeds.ra_resting_speed) if compensate_ra else AxisSpeeds.ra_resting_speed
			dec_dps = math.copysign(dps, AxisSpeeds.dec_resting_speed) if compensate_dec else AxisSpeeds.dec_resting_speed
			yield Maneuver(ra_dps, dec_dps, 'BL-compensation', duration)

	def steer(self, here, target, max_speed_dps=None, run_callback=None):
		"""
		Perform a steering maneuver from here to target,
		respecting a max speed given in degrees per second.

		Abort when run_callback returns false.
		"""
		maneuvers = self.get_steering_maneuvers(here, target, max_speed_dps)
		for maneuver in maneuvers:
			self.set_axis_speeds(
				ra_dps=maneuver.ra_dps,
				dec_dps=maneuver.dec_dps,
				mode=maneuver.mode,
			)
			if run_callback is not None:
				remain_time = maneuver.duration
				while remain_time > 0 and run_callback():
					time.sleep(min(remain_time, 1))
					remain_time -= 1
				if not run_callback():
					# no more maneuvers
					break
			else:
				time.sleep(maneuver.duration)
		self.set_resting()
