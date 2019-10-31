import sys
import glob
import argparse
import os
import json
import numpy as np

from image_stack_nebula import ImageStackNebula

from influxdb import InfluxDBClient


def query_offsets(path_prefix):
	# WIP
	# Usage: query_offsets('../beute/191013')
	path_prefix = path_prefix.replace('/', '\\/')
	influx_client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='tracking')
	offsets_query = f'SELECT ra_image_error, dec_image_error, file_path '\
					f'FROM axis_log WHERE file_path =~ /{path_prefix}*/ ORDER BY time ASC'

	offsets_result = influx_client.query(offsets_query)
	# it will remain influxDBs secret why this is so complicated
	rows = offsets_result.items()[0][1]
	return {row['file_path']: (row['ra_image_error'], row['dec_image_error']) for row in rows}



parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--out', type=str, default='stacked.png', help='Output filename')
parser.add_argument('--auto-crop', action='store_true', help='Crop the output image to highly sampled region')
parser.add_argument('--auto-crop-samples', type=int, default=None, help='Num samples to use as threshold for auto-crop')
parser.add_argument('--gamma', type=float, default=None, help='Gamma-correction value to apply')
parser.add_argument('--invert', action='store_true')
parser.add_argument('--range', type=str, default=None, help='Stack only given range of images, not all')
parser.add_argument('--darkframe-directory', type=str, default=None, help='Where to find darkframes')

args = parser.parse_args()

if args.darkframe_directory is not None:
	print(f'Handling darkframes from {args.darkframe_directory}')
	search_pattern = os.path.join(args.darkframe_directory, args.filename_pattern)
	darkframe_files = glob.glob(search_pattern)
	print(f'Found {len(darkframe_files)} darkframes - Creating an average frame')
	master_dark = ImageStackNebula.create_master_dark(args.darkframe_directory, darkframe_files)

print('Searching for files to stack')
search_pattern = os.path.join(args.directory, args.filename_pattern)
files = glob.glob(search_pattern)

if not files:
	print('No files. Use --filename-pattern if the images are not .tif')
	sys.exit(1)

print(f'Found {len(files)} files to stack. Consider --range if that\'s too many')
files.sort()

if args.range is not None:
	image_range = args.range.split(',')
	files = files[int(image_range[0]):int(image_range[1])]
	print(f'Only {len(files)} files selected for stacking')

print('Loading offsets from offsets.json')
frame_offsets = None
offsets_file = os.path.join(args.directory, 'offsets.json')
with open(offsets_file, 'r') as f:
	frame_offsets = json.load(f)

print('Stacking')
image = ImageStackNebula.from_files(args.directory, files, frame_offsets, master_dark)

if args.auto_crop:
	max_samples = np.amax(image.samples)
	print(f'Maximum number of samples per pixel is {max_samples}')
	min_samples = args.auto_crop_samples or max_samples
	print(f'Cropping image to region with at least {min_samples} samples')
	image.auto_crop(min_samples)

image.convert_to_grayscale()
image.normalize_samples()
image.normalize()

if args.gamma:
	image.apply_gamma(args.gamma)

if args.invert:
	image.invert()

image.save(args.out)
image.save_samples_map('samples_map.png')
