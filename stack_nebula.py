import sys
import glob
import argparse
import os
import json

from image_stack_nebula import ImageStackNebula


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--bits', type=int, default=16, help='Bits per channel to use while stacking. Use 16 (default) or 32.')
parser.add_argument('--out', type=str, default='stacked.png', help='Output filename')
parser.add_argument('--auto-crop', action='store_true', help='Crop the output image to fully exposed region')
parser.add_argument('--gamma', type=float, default=None, help='Gamma-correction value to apply')
parser.add_argument('--invert', action='store_true')
parser.add_argument('--range', type=str, default='0,-1', help='Stack only given range of images, not all')

args = parser.parse_args()

search_pattern = os.path.join(args.directory, args.filename_pattern)
files = glob.glob(search_pattern)

if not files:
	print('No files. Use --filename-pattern if the images are not .tif')
	sys.exit(1)

print(f'Found {len(files)} files')
files.sort()

image_range = args.range.split(',')
files = files[int(image_range[0]):int(image_range[1])]
print(f'Only {len(files)} files selected for stacking')

image = ImageStackNebula(args.directory, files, args.bits)

if args.auto_crop:
	image.auto_crop()
image.normalize()
if args.gamma:
	image.apply_gamma(args.gamma)
if args.invert:
	image.invert()
image.save(args.out)
