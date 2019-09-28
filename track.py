import sys
import serial
import glob
import argparse
import os
import time
import shutil
import numpy as np

from PIL import images 
from skimage.feature import register_translation


def load_frame_for_offset_detection(filename):
	pil_image = Image.open(filename).convert('L')
	yx_image = np.asarray(pil_image, dtype=np.int16)
	xy_image = np.transpose(yx_image, (1, 0))
	xy_image = np.clip(xy_image * 10, 128, 255)
	return xy_image


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--out-directory', type=str, default='.', help='Output directory to move images to')
parser.add_argument('--delay', type=int, default=1, help='Delay between images processed')
parser.add_argument('--usb-port', type=int, default=0, help='USB port to use for the motor control')

args = parser.parse_args()
search_pattern = os.path.join(args.directory, args.filename_pattern)

print('Re-creating output directory')
shutil.rmtree(args.out_directory, ignore_errors=True)
os.makedirs(args.out_directory)

offset_threshold = 50

# ra is about -0.215 when dec is perfect

ra_low, ra_high, ra_current, ra_invert = -0.2, -0.25, None, False
dec_low, dec_high, dec_current, dec_invert = 0.01, 0.05, None, False

port = f'/dev/ttyUSB{args.usb_port}'
serial = serial.Serial(port, 9600, timeout=1)

key_frame = None

def set_motor_speed(motor, speed):
	print(f'Setting motor {motor} speed to {speed} rev/s')
	serial.write(f'{speed}'.encode())

#set_motor_speed(350)
#time.sleep(60)
#sys.exit(1)

set_motor_speed('A', (ra_low + ra_high)/2)
set_motor_speed('B', (dec_low + dec_high)/2)

while True:
	time.sleep(args.delay/2)
	files = glob.glob(search_pattern)
	if not files:
		continue
	time.sleep(args.delay/2)

	files.sort()
	print(f'Found {len(files)} file(s), processing {os.path.basename(files[0])}')

	frame = load_frame_for_offset_detection(files[0])

	if key_frame is None:
		print('This shall be our reference frame.')
		key_frame = frame
	else:
		offset, _, __ = register_translation(key_frame, frame)
		print(f'Offset: {offset}')

		if abs(offset[0]) > offset_threshold:
			desired = ra_high if (offset[0] < 0 == ra_invert) else ra_low
			if ra_current != desired:
				set_motor_speed('A', desired)
				ra_current = desired

		if abs(offset[1]) > offset_threshold:
			desired = dec_high if (offset[1] < 0 == dec_invert) else dec_low
			if dec_current != desired:
				set_motor_speed('B', desired)
				dec_current = desired

	shutil.move(files[0], args.out_directory)
