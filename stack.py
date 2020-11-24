import argparse
import glob
import json
import numpy as np
import os
import sys

from lib.filter import Filter
from lib.frame import Frame
from lib.image_stack import ImageStack
from lib.util import create_average_frame, save_image

from skimage.filters import gaussian


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.png', help='Pattern to use when searching for input images')
parser.add_argument('--out', type=str, default='stacked.png', help='Output filename')
parser.add_argument('--auto-crop', action='store_true', help='Crop the output image to highly sampled region')
parser.add_argument('--auto-crop-samples', type=int, default=None, help='Num samples to use as threshold for auto-crop')
parser.add_argument('--gamma', type=float, default=None, help='Gamma-correction value to apply')
parser.add_argument('--invert', action='store_true')
parser.add_argument('--range', type=str, default=None, help='Stack only given range of images, not all')
parser.add_argument('--darks', type=str, default=None, help='Where to find dark frames')
parser.add_argument('--flats', type=str, default=None, help='Where to find flat frames')
parser.add_argument('--apply-function', action='store_true', help='Apply custom function to output image')
parser.add_argument('--color-mode', type=str, default='rgb', help='Options: grey, r, g, b, rgb')
parser.add_argument('--offset-filter', type=float, default=None, help='Filter out frames more than <angle> apart')
parser.add_argument('--custom-offset', type=str, default=None, help='Apply additional offset after alignment. Format: int,int')


args = parser.parse_args()

master_dark = create_average_frame(args.darks, args.filename_pattern, args.color_mode)
if master_dark is not None:
	save_image(master_dark * 4.0, 'out/master_dark.png')
average_flat = create_average_frame(args.flats, args.filename_pattern, args.color_mode)

if average_flat is not None:
	master_flat = average_flat / np.average(average_flat)
	# blur
	master_flat = gaussian(master_flat, sigma=4)

	save_image((master_flat - 1.0) * 256.0 + 128.0, 'out/master_flat.png')
else:
	master_flat = None


search_pattern = os.path.join(args.directory, args.filename_pattern)
files = glob.glob(search_pattern)

if not files:
	print('No files. Use --filename-pattern if the images are not .png')
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

print('Loading frame metadata')
metadata_file = os.path.join(args.directory, 'astrometric_metadata.json')
with open(metadata_file, 'r') as f:
	frame_metadata = json.load(f)

frames = [
	Frame(filepath, frame_metadata[os.path.basename(filepath)])
	for filepath in files
]

frames = Filter(args.offset_filter or 1.0).apply(frames)

# bake pixel offsets into frames
Frame.compute_frame_offsets(frames, args.custom_offset)
# interpolate angles 
Frame.interpolate_angles(frames)

print('Stacking...')
image = ImageStack.stack_frames(frames, args.color_mode, master_dark, master_flat)

if args.auto_crop:
	max_samples = np.amax(image.samples)
	print(f'Maximum number of samples per pixel is {max_samples}')
	min_samples = args.auto_crop_samples or max_samples
	print(f'Cropping image to region with at least {min_samples} samples')
	image.auto_crop(min_samples)

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

image.save(f'out/{args.out}')
image.save_samples_map('out/samples_map.png')
