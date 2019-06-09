import sys
import glob
import argparse
import os
import json

from stacked_image import StackedImage


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--offsets', type=str, default=None, help='Pixel-offset between first and last image. Format: <X>,<Y>')
parser.add_argument('--stride', type=int, default=1, help='Process only every Nth image')
parser.add_argument('--bits', type=int, default=16, help='Bits per channel to use while stacking. Use 16 (default) or 32.')
parser.add_argument('--out', type=str, default='stacked.png', help='Output filename')
parser.add_argument('--crop', type=str, default=None, help='Crop the image to a square with center X,Y. Format: <X>,<Y>,<Radius>')
parser.add_argument('--gamma', type=float, default=None, help='Gamma-correction value to apply')
parser.add_argument('--invert', action='store_true')

args = parser.parse_args()

search_pattern = os.path.join(args.directory, args.filename_pattern)
files = glob.glob(search_pattern)

if not files:
	print('No files. Use --filename-pattern if the images are not .tif')
	sys.exit(1)

print(f'Found {len(files)} files')
files.sort()

# default params
params = {
	'offsets': '0,0',
	'crop': None,
	'gamma': 1.0,
}

# params from file override defaults
params_file = os.path.join(args.directory, 'params.json')
if os.path.isfile(params_file):
	with open(params_file, 'r') as f:
		content = json.load(f)
		params.update(content)

# params from command line override everything
if args.offsets is not None:
	params.update({'offsets': args.offsets})
if args.crop is not None:
	params.update({'crop': args.crop})
if args.gamma is not None:
	params.update({'gamma': args.gamma})

print(f'Using params: {params}')

offsets = params['offsets'].split(',')
x_offset = int(offsets[0])
y_offset = int(offsets[1])

image = StackedImage(files, x_offset, y_offset, args.stride, args.bits)

if params['crop'] is not None:
	cx, cy, r = params['crop'].split(',')
	image.crop(int(cx), int(cy), int(r))

image.normalize()
image.substract_pollution()
image.normalize()
image.apply_gamma(params['gamma'])
if args.invert:
	image.invert()
image.save(args.out)

# write params back to disk
with open(params_file, 'w') as f:
	json.dump(params, f)
