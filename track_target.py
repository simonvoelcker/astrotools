import glob
import os
import time
import shutil
import math
import numpy as np

from datetime import datetime

from simple_pid import PID
from influxdb import InfluxDBClient

from axis_control import AxisControl
from util import locate_image


class Tracking:
	def __init__(self, config, image_search_pattern, axis_control):
		self.config = config
		self.image_search_pattern = image_search_pattern

		self.target = None
		self.axis_control = axis_control
		self.influx_client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='tracking')

		self.ra_pid = PID(self.config['ra']['pid_p'], self.config['ra']['pid_i'], self.config['ra']['pid_d'], setpoint=0)
		self.ra_pid.output_limits = (-self.config['ra']['range'], self.config['ra']['range'])
		self.ra_pid.sample_time = self.config['sample_time']

		self.dec_pid = PID(self.config['dec']['pid_p'], self.config['dec']['pid_i'], self.config['dec']['pid_d'], setpoint=0)
		self.dec_pid.output_limits = (-self.config['dec']['range'], self.config['dec']['range'])
		self.dec_pid.sample_time = self.config['sample_time']

	def write_frame_stats(self, **kwargs):
		time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%Z')
		body = [
		    {
		        'measurement': 'axis_log',
		        'tags': {
		            'source': 'track.py',
		        },
		        'time': time,
		        'fields': kwargs, 
		    }
		]
		self.influx_client.write_points(body)

	def track_target(self, target):
		self.target = target
		known_files = set(glob.glob(self.image_search_pattern))

		while True:
			all_files = set(glob.glob(self.image_search_pattern))
			new_files = all_files - known_files
			time.sleep(0.5)  # wait here, not above, to be sure the new file is complete on disk
			if not new_files:
				continue
			known_files = all_files
			if len(new_files) > 1:
				print(f'WARN: Found {len(new_files)} new images at once')
			newest_file = max(new_files, key=os.path.getctime)
			print(f'Handling new file: {newest_file}')
			self.on_new_file(newest_file)

	def get_tracking_mode_config(self, ra_error, dec_error):
		# get the appropriate tracking mode config for the current error
		total_error = math.hypot(ra_error, dec_error)
		for mode_config in self.config['modes']:
			max_error = mode_config['max_error_deg']
			if max_error is None or total_error <= max_error:
				print(f'RA err: {ra_error:.2f}, Dec err: {dec_error:.2f}, '\
					  f'Total err: {total_error:.2f} => Mode: {mode_config["name"]}')
				return mode_config
		print(f'Warn: Found no tracking mode config for total err: {total_error}')
		return None

	def on_new_file(self, file_path):
		image_coordinates = locate_image(file_path)
		if not image_coordinates:
			print(f'Failed to locate: {file_path}. Falling back to resting speed.')
			self.axis_control.set_motor_speed('A', AxisControl.ra_resting_speed)		
			self.axis_control.set_motor_speed('B', AxisControl.dec_resting_speed)
			return

		ra_error = image_coordinates.ra - self.target.ra
		dec_error = image_coordinates.dec - self.target.dec

		mode_config = self.get_tracking_mode_config(ra_error, dec_error)

		if 'Steering' in mode_config['name']:
			self.axis_control.steer(
				here=image_coordinates,
				target=self.target,
				max_speed_dps=mode_config['max_speed_dps'],
			)
			print('Waiting for axes to settle')
			time.sleep(mode_config['delay_after_maneuver_sec'])
			return

		ra_speed = self.config['ra']['center'] + self.ra_pid(-ra_error if self.config['ra']['invert'] else ra_error)
		dec_speed = self.config['dec']['center'] + self.dec_pid(-dec_error if self.config['dec']['invert'] else dec_error)

		print(f'RA error: {ra_error:8.6f}, DEC error: {dec_error:8.6f}, '\
			  f'RA speed: {ra_speed:8.6f}, DEC speed: {dec_speed:8.6f}')
		
		self.axis_control.set_motor_speed('A', ra_speed)		
		self.axis_control.set_motor_speed('B', dec_speed)

		if self.influx_client is not None:
			self.write_frame_stats(
				file_path=file_path,
				ra_image_error=float(ra_error),
				ra_speed=float(ra_speed),
				ra_pid_p=float(self.ra_pid.components[0]),
				ra_pid_i=float(self.ra_pid.components[1]),
				ra_pid_d=float(self.ra_pid.components[2]),
				dec_image_error=float(dec_error),
				dec_speed=float(dec_speed),
				dec_pid_p=float(self.dec_pid.components[0]),
				dec_pid_i=float(self.dec_pid.components[1]),
				dec_pid_d=float(self.dec_pid.components[2]),
			)
