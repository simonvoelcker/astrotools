import sys
import glob
import argparse
import os
import json
import numpy as np

from image_stack_nebula import ImageStackNebula
from util import create_average_frame, save_image


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--out', type=str, default='stacked.png', help='Output filename')
parser.add_argument('--auto-crop', action='store_true', help='Crop the output image to highly sampled region')
parser.add_argument('--auto-crop-samples', type=int, default=None, help='Num samples to use as threshold for auto-crop')
parser.add_argument('--gamma', type=float, default=None, help='Gamma-correction value to apply')
parser.add_argument('--invert', action='store_true')
parser.add_argument('--range', type=str, default=None, help='Stack only given range of images, not all')
parser.add_argument('--darks', type=str, default=None, help='Where to find dark frames')
parser.add_argument('--flats', type=str, default=None, help='Where to find flat frames')
parser.add_argument('--biases', type=str, default=None, help='Where to find bias frames')
parser.add_argument('--apply-function', action='store_true', help='Apply custom function to output image')
parser.add_argument('--color-mode', type=str, default='rgb', help='Options: grey, r, g, b, rgb')

args = parser.parse_args()

master_dark = create_average_frame(args.darks, args.filename_pattern, args.color_mode)
if master_dark is not None:
	save_image(master_dark * 64.0, 'master_dark.png')
average_flat = create_average_frame(args.flats, args.filename_pattern, args.color_mode)
average_bias = create_average_frame(args.biases, args.filename_pattern, args.color_mode)

if average_flat is not None and average_bias is not None:
	average_flat -= average_bias
	master_flat = average_flat / np.average(average_flat)
	save_image(average_bias * 64.0, 'average_bias.png')
	save_image((master_flat - 1.0) * 1500.0 + 128.0, 'master_flat.png')
else:
	master_flat = None


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

# print('Loading offsets from offsets.json')
# frame_offsets = None
# offsets_file = os.path.join(args.directory, 'offsets.json')
# with open(offsets_file, 'r') as f:
# 	frame_offsets = json.load(f)

print('Loading offsets from astrometric_metadata.json')
astrometric_metadata = None
metadata_file = os.path.join(args.directory, 'astrometric_metadata.json')
with open(metadata_file, 'r') as f:
	astrometric_metadata = json.load(f)

print('Stacking...')
image = ImageStackNebula.from_files(
	files,
	astrometric_metadata,
	args.color_mode,
	master_dark,
	master_flat,
)

if args.auto_crop:
	max_samples = np.amax(image.samples)
	print(f'Maximum number of samples per pixel is {max_samples}')
	min_samples = args.auto_crop_samples or max_samples
	print(f'Cropping image to region with at least {min_samples} samples')
	image.auto_crop(min_samples)

image.normalize_samples()
image.normalize()

if args.gamma:
	image.apply_gamma(args.gamma)

def f(p):
	low = 40.0/255.0
	high = 100.0/255.0
	if p <= low:
		return 0.0
	if p >= high:
		return 1.0
	return (p-low) / (high-low)

if args.apply_function:
	image.apply_function(f)

if args.invert:
	image.invert()

image.save(args.out)
image.save_samples_map('samples_map.png')
