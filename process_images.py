import sys
import glob
import argparse
import os
import time
import shutil
import numpy as np

from util import load_image, save_image
from sharpness import get_sharpness


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--out-directory', type=str, default='.', help='Output directory')
parser.add_argument('--delay', type=int, default=1, help='Delay between images processed')

args = parser.parse_args()
search_pattern = os.path.join(args.directory, args.filename_pattern)


def process_file(file):
	image = load_image(file, dtype=np.int16)
	sharpness = get_sharpness(image[:,:,0])
	print(f'Sharpness is {sharpness}')


while True:
	time.sleep(args.delay)
	files = glob.glob(search_pattern)
	if not files:
		continue

	files.sort()
	print(f'Found {len(files)} file(s), processing {os.path.basename(files[0])}')

	process_file(files[0])
	shutil.move(files[0], args.out_directory)
