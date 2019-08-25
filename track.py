import sys
import serial
import glob
import argparse
import os
import time
import shutil
import numpy as np

from util import load_image
from skimage.feature import register_translation


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--out-directory', type=str, default='.', help='Output directory to move images to')
parser.add_argument('--delay', type=int, default=1, help='Delay between images processed')

args = parser.parse_args()
search_pattern = os.path.join(args.directory, args.filename_pattern)

print('Re-creating output directory')
shutil.rmtree(args.out_directory, ignore_errors=True)
os.makedirs(args.out_directory)


track_axis = 1
offset_threshold = 100

# these are delays, so speed is inverted
low_speed = 500
high_speed = 300
current_speed = None

ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
key_frame = None


def set_motor_speed(speed):
	print(f'Setting motor speed to {speed}')
	ser.write(f'{speed}'.encode())

set_motor_speed((low_speed + high_speed)/2)

while True:
	time.sleep(args.delay)
	files = glob.glob(search_pattern)
	if not files:
		continue

	files.sort()
	print(f'Found {len(files)} file(s), processing {os.path.basename(files[0])}')

	frame = load_image(files[0], dtype=np.int16)

	if key_frame is None:
		print('This shall be our reference frame.')
		key_frame = frame
	else:
		offset, _, __ = register_translation(key_frame[:,:,1], frame[:,:,1])
		print(f'Offset: {offset}')

		if abs(offset[track_axis]) > offset_threshold:
			desired_speed = high_speed if offset[track_axis] < 0 else low_speed
			if current_speed != desired_speed:
				set_motor_speed(desired_speed)
				current_speed = desired_speed

	shutil.move(files[0], args.out_directory)
