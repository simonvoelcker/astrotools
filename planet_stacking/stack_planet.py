import sys
import glob
import argparse
import os
import json
import numpy as np

from PIL import Image
from image_stack import ImageStack


def load_frame(filename, dtype):
	pil_image = Image.open(filename)
	yxc_image = np.asarray(pil_image, dtype=dtype)
	xyc_image = np.transpose(yxc_image, (1, 0, 2))
	return xyc_image

def create_image_stack(directory, bits, crop_input):
	# read offsets files
	offsets_file = os.path.join(directory, 'offsets.json')
	with open(offsets_file, 'r') as f:
		frame_offsets = json.load(f)

	dtype = np.int16 if bits == 16 else np.int32

	crop_x, crop_y, crop_r = crop_input.split(',')
	crop_x, crop_y, crop_r = int(crop_x), int(crop_y), int(crop_r)

	frames = []
	for filename, (offset_x,offset_y) in frame_offsets.items():

		filename = os.path.join(directory, filename)
		full_frame = load_frame(filename, dtype)

		frame = full_frame[offset_x+crop_x-crop_r:offset_x+crop_x+crop_r, offset_y+crop_y-crop_r:offset_y+crop_y+crop_r, :]

		if frame.shape != (2*crop_r, 2*crop_r, frame.shape[2]):
			print(f'Skipping frame because of bad shape: {frame.shape}')

		frames.append(frame)

	if not len(frames):
		print('Warn: No frames')
		return

	return ImageStack(frames)


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)

parser.add_argument('--bits', type=int, default=16, help='Bits per channel to use while stacking. Use 16 (default) or 32.')
parser.add_argument('--crop-input', type=str, default=None, help='Crop the input images to a square with center X,Y. Format: <X>,<Y>,<Radius>')
parser.add_argument('--gamma', type=float, default=None, help='Gamma-correction value to apply')
parser.add_argument('--invert', action='store_true')
parser.add_argument('--out', type=str, default='stacked.png', help='Output filename')

args = parser.parse_args()

image = create_image_stack(args.directory, args.bits, args.crop_input)

image.normalize()
if args.gamma is not None:
	image.apply_gamma(float(args.gamma))
if args.invert:
	image.invert()

image.save(args.out)
