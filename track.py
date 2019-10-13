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
	print(f'Setting motor {motor} speed to {speed} rev/s')
	if serial is not None:
		serial.write(f'{speed}'.encode())


parser = argparse.ArgumentParser()
parser.add_argument('--incoming', type=str, default=os.path.join('..', 'beute', '**'))
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--clear-input', type=bool, default=True, help='Move any input images found at startup elsewhere')
parser.add_argument('--delay', type=float, default=1.0, help='Delay between images processed, in seconds')
parser.add_argument('--usb-port', type=int, default=0, help='USB port to use for the motor control')
parser.add_argument('--no-control', action='store_true', help='Do not actually connect to the motor control')

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
	port = f'/dev/ttyUSB{args.usb_port}'
	try:
		serial = serial.Serial(port, 9600, timeout=1)
	except serial.serialutil.SerialException:
		print('Failed to connect. Try --usb-port=1 or use --no-control.')
		exit(1)

kP, kI, kD = 0.00005, 0, 0.0001

ra_pid = PID(kP, kI, kD, setpoint=0)
ra_pid.output_limits = (-0.0028, -0.002)
ra_pid.sample_time = args.delay

dec_pid = PID(kP, kI, kD, setpoint=0)
dec_pid.output_limits = (0.0, 0.001)
dec_pid.sample_time = args.delay

ra_invert, dec_invert = True, False

set_motor_speed(serial, 'A', -0.0024)
set_motor_speed(serial, 'B', 0.0)

reference_frame = None
while True:
	files = glob.glob(search_pattern)
	if not files:
		time.sleep(1.0)
		continue

	if len(files) > 1:
		print(f'WARN: Found {len(files)} files, processing only one at a time')
		files.sort()

	frame = load_frame_for_offset_detection(files[0])

	if reference_frame is None:
		reference_frame = frame
	else:
		(ra_error, dec_error), _, __ = register_translation(reference_frame, frame)
		print(f'RA error: {ra_error}, DEC error: {dec_error}')
		ra_speed = ra_pid(-ra_error if ra_invert else ra_error)
		set_motor_speed(serial, 'A', ra_speed)
		
		dec_speed = dec_pid(-dec_error if dec_invert else dec_error)
		set_motor_speed(serial, 'B', dec_speed)

	shutil.move(files[0], out_directory)
	time.sleep(arg.delay-1.0)