import sys
import glob
import argparse
import os
import json

from alignment import Alignment
from util import load_image_greyscale


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--max-frame-distance', type=int, default=480, help='Maximum cartesian distance between frames, in pixels')
parser.add_argument('--range', type=str, default=None, help='Stack only given range of images, not all')
parser.add_argument('--amplification', type=int, default=5, help='Multiply images by this number before offset detection')
parser.add_argument('--threshold', type=int, default=128, help='Clip images by this brightness value after amplification')
parser.add_argument('--dryrun', action='store_true', help='Do not write any output except on the console')

args = parser.parse_args()

search_pattern = os.path.join(args.directory, args.filename_pattern)
files = glob.glob(search_pattern)

if not files:
	print('No files. Use --filename-pattern if the images are not .tif')
	sys.exit(1)

print(f'Found {len(files)} files')
files.sort()

if args.range is not None:
	image_range = args.range.split(',')
	files = files[int(image_range[0]):int(image_range[1])]
	print(f'Only {len(files)} files selected for offset detection')

alignment = Alignment(args.amplification, args.threshold, args.max_frame_distance)

frame_offsets_by_file = dict()	# map filename to offsets tuple
for frame_index, file in enumerate(files):
	frame = load_image_greyscale(file)
	offsets = alignment.get_offsets(frame, frame_index)
	frame_offsets_by_file[os.path.basename(file)] = offsets

if not args.dryrun:
	offsets_file = os.path.join(args.directory, 'offsets.json')
	with open(offsets_file, 'w') as f:
		json.dump(frame_offsets_by_file, f, indent=4, sort_keys=True)

	alignment.create_plot(title='Image offset distribution', filename='image_offsets.png')
