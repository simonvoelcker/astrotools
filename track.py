import sys
import serial
import glob
import argparse
import os
import time
import shutil
import datetime
import numpy as np

from PIL import Image
from skimage.feature import register_translation
from simple_pid import PID


def load_frame_for_offset_detection(filename):
	pil_image = Image.open(filename).convert('L')
	yx_image = np.asarray(pil_image, dtype=np.int16)
	xy_image = np.transpose(yx_image, (1, 0))
	xy_image = np.clip(xy_image * 10, 128, 255)
	return xy_image


def set_motor_speed(serial, motor, speed):
	if serial is not None:
		serial.write(f'{speed}'.encode())
		time.sleep(1)
		print(serial.in_waiting)

port = f'/dev/ttyUSB0'
serial = serial.Serial(port, 9600, timeout=5)
set_motor_speed(serial, 'A', 0.1)
time.sleep(1.0)
set_motor_speed(serial, 'A', 0.1)

exit(0)

parser = argparse.ArgumentParser()
parser.add_argument('--incoming', type=str, default=os.path.join('..', 'beute', '**'))
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--usb-port', type=int, default=0, help='USB port to use for the motor control')
parser.add_argument('--no-control', action='store_true', help='Do not actually connect to the motor control')
parser.add_argument('--delay', type=float, default=1.0, help='Delay between images processed, in seconds')

args = parser.parse_args()
search_pattern = os.path.join(args.incoming, args.filename_pattern)

files = glob.glob(search_pattern)
if files:
	leftovers_directory = datetime.datetime.now().strftime('untracked_%Y%m%d_%H%M%S')
	print(f'Found {len(files)} files at startup, moving them to {leftovers_directory}')
	os.makedirs(leftovers_directory)
	for file in files:
		shutil.move(file, leftovers_directory)

out_directory = datetime.datetime.now().strftime('tracked_%Y%m%d_%H%M%S')
os.makedirs(out_directory)

if args.no_control:
	serial = None
else:
	try:
		port = f'/dev/ttyUSB{args.usb_port}'
		serial = serial.Serial(port, 9600, timeout=5)
	except serial.serialutil.SerialException:
		print('Failed to connect. Try --usb-port=1 or use --no-control.')
		exit(1)

kP, kI, kD = 0.00005, 0, 0.0001
ra_low, ra_high = -0.005, 0.0
dec_low, dec_high = 0.0, 0.003
ra_invert, dec_invert = True, True

ra_pid = PID(kP, kI, kD, setpoint=0)
ra_pid.output_limits = (ra_low, ra_high)
ra_pid.sample_time = args.delay

dec_pid = PID(kP, kI, kD, setpoint=0)
dec_pid.output_limits = (dec_low, dec_high)
dec_pid.sample_time = args.delay

print(f'Setting initial motor speeds')
set_motor_speed(serial, 'A', (ra_low+ra_high)/2.0)
set_motor_speed(serial, 'B', (dec_low+dec_high)/2.0)

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

		print(f'RA error: {int(ra_error):4}, DEC error: {int(dec_error):4}, RA speed: {ra_speed:8.5f}, DEC speed: {dec_speed:8.5f}')

		set_motor_speed(serial, 'A', ra_speed)		
		set_motor_speed(serial, 'B', dec_speed)

	shutil.move(files[0], out_directory)
	time.sleep(args.delay-1.0)