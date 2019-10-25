import re
import sys
import serial
import glob
import argparse
import os
import time
import shutil
import numpy as np

from datetime import datetime, timedelta

from PIL import Image
from skimage.feature import register_translation
from simple_pid import PID
from influxdb import InfluxDBClient
from sharpness import get_sharpness


control_response_re = r'\s*M(?P<motor>[12])\s+S=(?P<speed>\-?\d+\.\d+)\s+P1=(?P<P1>\-?\d+)\s+P2=(?P<P2>\-?\d+)\s*'
control_response_rx = re.compile(control_response_re)


def load_frame_for_offset_detection(filename):
	pil_image = Image.open(filename).convert('L')
	yx_image = np.asarray(pil_image, dtype=np.int16)
	xy_image = np.transpose(yx_image, (1, 0))
	xy_image = np.clip(xy_image * 5, 128, 255)
	return xy_image


def connect_serial(args):
	if args.usb_port is None:
		return None
	for port in [args.usb_port, 1-args.usb_port]:
		try:
			ser = serial.Serial(f'/dev/ttyUSB{port}', 9600, timeout=2)
			# connection cannot be used immediately ...yes, i know.
			time.sleep(2)
			return ser
		except serial.serialutil.SerialException:
			print(f'Failed to connect on port {port}.')
	exit(1)


def set_motor_speed(serial, motor, speed):
	if serial is not None:
		msg = f'{motor}{speed:9.6f}'
		serial.write(msg.encode())
		return 0, 0
		
		# readback takes a second
		response = serial.readline().decode()
		match = control_response_rx.match(response)
		if not match:
			print('Failed to parse response from the motor control!')
			print(response)
			exit()
		return match.group('P1'), match.group('P2')


influx_client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='tracking')

def write_frame_stats(ra_position, ra_speed, ra_image_error, dec_position, dec_speed, dec_image_error, sharpness):
	time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%Z')
	body = [
	    {
	        'measurement': 'axis_log',
	        'tags': {
	            'source': 'track.py',
	        },
	        'time': time,
	        'fields': {
	            'ra_position': float(ra_position),
	            'ra_speed': float(ra_speed),
	            'ra_image_error': float(ra_image_error),
	            'dec_position': float(dec_position),
	            'dec_speed': float(dec_speed),
	            'dec_image_error': float(dec_image_error),
	            'sharpness': float(sharpness),
	        }
	    }
	]
	influx_client.write_points(body)

parser = argparse.ArgumentParser()
parser.add_argument('--incoming', type=str, default=os.path.join('..', 'beute', '**'))
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--usb-port', type=int, default=None, help='USB port to use for the motor control')
parser.add_argument('--delay', type=float, default=1.0, help='Delay between images processed, in seconds')

args = parser.parse_args()
search_pattern = os.path.join(args.incoming, args.filename_pattern)

files = glob.glob(search_pattern)
if files:
	leftovers_directory = datetime.now().strftime('untracked_%Y%m%d_%H%M%S')
	leftovers_directory = os.path.join('..', 'processed', leftovers_directory)
	print(f'Found {len(files)} files at startup, moving them to {leftovers_directory}')
	os.makedirs(leftovers_directory)
	for file in files:
		shutil.move(file, leftovers_directory)

out_directory = datetime.now().strftime('tracked_%Y%m%d_%H%M%S')
out_directory = os.path.join('..', 'processed', out_directory)
os.makedirs(out_directory)

ser = connect_serial(args)

ra_low, ra_high = -0.24, -0.2
dec_low, dec_high = -0.001, 0.0
ra_invert, dec_invert = True, True

ra_pid = PID(0.002, 0.0, 0.001, setpoint=0)
ra_pid.output_limits = (ra_low, ra_high)
ra_pid.sample_time = args.delay

dec_pid = PID(0.00005, 0, 0.0001, setpoint=0)
dec_pid.output_limits = (dec_low, dec_high)
dec_pid.sample_time = args.delay

print(f'Setting initial motor speeds')
set_motor_speed(ser, 'A', (ra_low+ra_high)/2.0)
set_motor_speed(ser, 'B', (dec_low+dec_high)/2.0)

reference_frame = None
while True:
	files = glob.glob(search_pattern)
	time.sleep(0.5)
	if not files:
		continue

	if len(files) > 1:
		print(f'WARN: Found {len(files)} files, consider fiddling around with --delay.')
		files.sort()

	frame = load_frame_for_offset_detection(files[0])

	if reference_frame is None:
		reference_frame = frame
	else:
		(ra_error, dec_error), _, __ = register_translation(reference_frame, frame)
		ra_speed = ra_pid(-ra_error if ra_invert else ra_error)
		dec_speed = dec_pid(-dec_error if dec_invert else dec_error)
		set_motor_speed(ser, 'A', ra_speed)		
		ra_position, dec_position = set_motor_speed(ser, 'B', dec_speed)

		sharpness = get_sharpness(frame)

		print(
			f'RA error: {int(ra_error):4}, '\
			f'DEC error: {int(dec_error):4}, '\
			f'RA speed: {ra_speed:8.5f}, '\
			f'DEC speed: {dec_speed:8.5f}, '\
			f'RA pos: {int(ra_position):8}, '\
			f'DEC pos: {int(dec_position):8} '\
			f'SHRP: {sharpness}'
		)
		write_frame_stats(ra_position, ra_speed, ra_error, dec_position, dec_speed, dec_error, sharpness)

	shutil.move(files[0], out_directory)
