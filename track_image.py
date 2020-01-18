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
from util import load_image
from axis_control import AxisControl

config = {
	'ra_center': -0.0047,
	'ra_range': 0.001,
	'ra_invert': True,
	'ra_pid_p': 0.00002,
	'ra_pid_i': 0.0,
	'ra_pid_d': 0.0002,
	
	'dec_center': 0.0,
	'dec_range': 0.001,
	'dec_invert': True,
	'dec_pid_p': 0.00001,
	'dec_pid_i': 0.0,
	'dec_pid_d': 0.001,

	'sample_time': 10.0,
}


def write_frame_stats(**kwargs):
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
	influx_client.write_points(body)

parser = argparse.ArgumentParser()
parser.add_argument('--incoming', type=str, default=os.path.join('..', 'beute', '**'))
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--delay', type=float, default=1.0, help='Delay between images processed, in seconds')
parser.add_argument('--no-stats', action='store_true', help='Do not send stats to InfluxDB')
parser.add_argument('--preview', type=int, default=None, help='Write preview of last N frames')
parser.add_argument('--usb-port', type=int, default=None, help='USB port to use for the motor control. Omit for no motor control.')
parser.add_argument('--keep-untracked', action='store_true', help='Move files found on startup somewhere instead of removing them')
parser.add_argument('--image-amplification', type=int, default=1, help='Multiply images by this number for offset detection')

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
ra_pid.output_limits = (-config['ra_range'], config['ra_range'])
ra_pid.sample_time = args.delay

dec_pid = PID(config['dec_pid_p'], config['dec_pid_i'], config['dec_pid_d'], setpoint=0)
dec_pid.output_limits = (-config['dec_range'], config['dec_range'])
dec_pid.sample_time = args.delay

axis_control = None
if args.usb_port is not None:
	# Try both USB (my) ports. They keep switching randomly and I want to be lazy.
	axis_control = AxisControl()
	axis_control.connect(usb_ports=[0,1])
	print(f'Setting initial motor speeds')
	axis_control.set_motor_speed('A', config['ra_center'])
	axis_control.set_motor_speed('B', config['dec_center'])
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
	frame_for_offset_detection = np.clip(frame_greyscale * args.image_amplification, 128, 255)

	if reference_frame is None:
		reference_frame = frame_for_offset_detection
	else:
		(ra_error, dec_error), _, __ = register_translation(reference_frame, frame_for_offset_detection)
		ra_speed = config['ra_center'] + ra_pid(-ra_error if config['ra_invert'] else ra_error)
		dec_speed = config['dec_center'] + dec_pid(-dec_error if config['dec_invert'] else dec_error)

		if axis_control is not None:
			axis_control.set_motor_speed('A', ra_speed)		
			axis_control.set_motor_speed('B', dec_speed)

		print(
			f'RA error: {int(ra_error):4}, '\
			f'DEC error: {int(dec_error):4}, '\
			f'RA speed: {ra_speed:8.5f}, '\
			f'DEC speed: {dec_speed:8.5f}'
		)

		if influx_client is not None:
			write_frame_stats(
				file_path=files[0],
				ra_image_error=float(ra_error),
				ra_speed=float(ra_speed),
				ra_pid_p=float(ra_pid.components[0]),
				ra_pid_i=float(ra_pid.components[1]),
				ra_pid_d=float(ra_pid.components[2]),
				dec_image_error=float(dec_error),
				dec_speed=float(dec_speed),
				dec_pid_p=float(dec_pid.components[0]),
				dec_pid_i=float(dec_pid.components[1]),
				dec_pid_d=float(dec_pid.components[2]),
			)

		if preview is not None:
			preview.update(frame, (ra_error, dec_error))

	shutil.move(files[0], out_directory)
