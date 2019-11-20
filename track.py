import glob
import argparse
import os
import time
import shutil
import numpy as np

from datetime import datetime

from skimage.feature import register_translation
from simple_pid import PID
from influxdb import InfluxDBClient

from preview import Preview
from util import load_image, get_sharpness_values
from steer import AxisControl

config = {
	'ra_low': -0.005,
	'ra_high': -0.004,
	'ra_invert': True,
	'dec_low': -0.002,
	'dec_high': 0.0,
	'dec_invert': True,
	
	'ra_pid_p': 0.00004,
	'ra_pid_i': 0.000001,
	'ra_pid_d': 0.00004,
	'dec_pid_p': 0.00005,
	'dec_pid_i': 0.000001,
	'dec_pid_d': 0.0001,

	'sample_time': 10.0,
}


def write_frame_stats(file_path, ra_position, ra_speed, ra_image_error, dec_position, dec_speed, dec_image_error, sharpness_values):
	time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%Z')
	body = [
	    {
	        'measurement': 'axis_log',
	        'tags': {
	            'source': 'track.py',
	        },
	        'time': time,
	        'fields': {
	        	'file_path': file_path,
	            'ra_position': float(ra_position),
	            'ra_speed': float(ra_speed),
	            'ra_image_error': float(ra_image_error),
	            'dec_position': float(dec_position),
	            'dec_speed': float(dec_speed),
	            'dec_image_error': float(dec_image_error),
	            'sharpness': float(sharpness_values['sharpness']),
	            'sharpness_x': float(sharpness_values['sharpness_x']),
	            'sharpness_y': float(sharpness_values['sharpness_y']),
	        }
	    }
	]
	influx_client.write_points(body)

parser = argparse.ArgumentParser()
parser.add_argument('--incoming', type=str, default=os.path.join('..', 'beute', '**'))
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--delay', type=float, default=1.0, help='Delay between images processed, in seconds')
parser.add_argument('--no-stats', action='store_true', help='Do not send stats to InfluxDB')
parser.add_argument('--preview', type=int, default=None, help='Write preview of last N frames')
parser.add_argument('--usb-port', type=int, default=None, help='USB port to use for the motor control. Omit for no motor control.')
parser.add_argument('--keep-untracked', action='store_true', help='Move files found on startup somewhere instead of removing them')

args = parser.parse_args()
search_pattern = os.path.join(args.incoming, args.filename_pattern)

files = glob.glob(search_pattern)
if files:
	print(f'Found {len(files)} files at startup')
	if args.keep_untracked:
		leftovers_directory = datetime.now().strftime('untracked_%Y%m%d_%H%M%S')
		leftovers_directory = os.path.join('..', 'processed', leftovers_directory)
		print(f'Moving them to {leftovers_directory}')
		os.makedirs(leftovers_directory)
		for file in files:
			shutil.move(file, leftovers_directory)
	else:
		print('Removing them. Consider using --keep-untracked if that was not okay')
		for file in files:
			os.remove(file)

out_directory = datetime.now().strftime('tracked_%Y%m%d_%H%M%S')
out_directory = os.path.join('..', 'processed', out_directory)
os.makedirs(out_directory)

preview = None
if args.preview is not None:
	preview = Preview(num_frames=args.preview)

influx_client = None
if not args.no_stats:
	influx_client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='tracking')

ra_pid = PID(config['ra_pid_p'], config['ra_pid_i'], config['ra_pid_d'], setpoint=0)
ra_pid.output_limits = (config['ra_low'], config['ra_high'])
ra_pid.sample_time = args.delay

dec_pid = PID(config['dec_pid_p'], config['dec_pid_i'], config['dec_pid_d'], setpoint=0)
dec_pid.output_limits = (config['dec_low'], config['dec_high'])
dec_pid.sample_time = args.delay

axis_control = None
if args.usb_port is not None:
	# Try both USB (my) ports. They keep switching randomly and I want to be lazy.
	axis_control = AxisControl([args.usb_port, 1-args.usb_port])
	print(f'Setting initial motor speeds')
	axis_control.set_motor_speed('A', (config['ra_low']+config['ra_high'])/2.0)
	axis_control.set_motor_speed('B', (config['dec_low']+config['dec_high'])/2.0)
else:
	print('Not connecting to motor control. Consider using --usb-port.')


reference_frame = None

while True:
	files = glob.glob(search_pattern)
	time.sleep(0.5)
	if not files:
		continue

	if len(files) > 1:
		print(f'WARN: Found {len(files)} files, consider fiddling around with --delay.')
		files.sort()

	# original frame - all color channels
	frame = load_image(files[0], dtype=np.int16)
	# greyscale frame, only width and height
	frame_greyscale = np.mean(frame, axis=2)
	# the same, but optimized for offset-detection
	frame_for_offset_detection = np.clip(frame_greyscale * 5, 128, 255)

	if reference_frame is None:
		reference_frame = frame_for_offset_detection
	else:
		(ra_error, dec_error), _, __ = register_translation(reference_frame, frame_for_offset_detection)
		ra_speed = ra_pid(-ra_error if config['ra_invert'] else ra_error)
		dec_speed = dec_pid(-dec_error if config['dec_invert'] else dec_error)

		# position readback takes a second - skip for now
		ra_position, dec_position = 0, 0

		if axis_control is not None:
			axis_control.set_motor_speed('A', ra_speed)		
			axis_control.set_motor_speed('B', dec_speed)

		sharpness_values = get_sharpness_values(frame_greyscale)

		print(
			f'RA error: {int(ra_error):4}, '\
			f'DEC error: {int(dec_error):4}, '\
			f'RA speed: {ra_speed:8.5f}, '\
			f'DEC speed: {dec_speed:8.5f}, '\
			f'RA pos: {int(ra_position):8}, '\
			f'DEC pos: {int(dec_position):8} '\
			f'SHRP: {sharpness_values["sharpness"]}'
		)

		if influx_client is not None:
			write_frame_stats(files[0], ra_position, ra_speed, ra_error, dec_position, dec_speed, dec_error, sharpness_values)

		if preview is not None:
			preview.update(frame, (ra_error, dec_error))

	shutil.move(files[0], out_directory)
