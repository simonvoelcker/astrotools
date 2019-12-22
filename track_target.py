import glob
import os
import time
import shutil
import numpy as np

from datetime import datetime

from simple_pid import PID
from influxdb import InfluxDBClient

from steer import AxisControl
from util import locate_image


class Tracking:
	config = {
		'ra_center': -0.0047,
		'ra_range': 0.001,
		'ra_invert': False,
		'ra_pid_p': 0.002,
		'ra_pid_i': 0.0,
		'ra_pid_d': 0.0,
		
		'dec_center': 0.0,
		'dec_range': 0.0005,
		'dec_invert': True,
		'dec_pid_p': 0.05,
		'dec_pid_i': 0.0,
		'dec_pid_d': 0.0,

		'sample_time': 10.0,
	}

	def __init__(self, image_search_pattern, delay, axis_control):
		self.image_search_pattern = image_search_pattern
		self.delay = delay
		self.target = None
		self.axis_control = axis_control
		self.influx_client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='tracking')

		self.ra_pid = PID(self.config['ra_pid_p'], self.config['ra_pid_i'], self.config['ra_pid_d'], setpoint=0)
		self.ra_pid.output_limits = (-self.config['ra_range'], self.config['ra_range'])
		self.ra_pid.sample_time = self.delay

		self.dec_pid = PID(self.config['dec_pid_p'], self.config['dec_pid_i'], self.config['dec_pid_d'], setpoint=0)
		self.dec_pid.output_limits = (-self.config['dec_range'], self.config['dec_range'])
		self.dec_pid.sample_time = self.delay

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

	def on_new_file(self, file_path):
		image_coordinates = locate_image(file_path, cpulimit=self.delay)
		if not image_coordinates:
			print(f'Failed to locate: {file_path}')
			return

		ra_error = image_coordinates.ra - self.target.ra
		dec_error = image_coordinates.dec - self.target.dec

		print(f'image: {image_coordinates} target: {self.target}')

		ra_speed = self.config['ra_center'] + self.ra_pid(-ra_error if self.config['ra_invert'] else ra_error)
		dec_speed = self.config['dec_center'] + self.dec_pid(-dec_error if self.config['dec_invert'] else dec_error)

		self.axis_control.set_motor_speed('A', ra_speed)		
		self.axis_control.set_motor_speed('B', dec_speed)

		print(f'RA error: {ra_error:8.6f}, DEC error: {dec_error:8.6f}, '\
			  f'RA speed: {ra_speed:8.6f}, DEC speed: {dec_speed:8.6f}')

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
