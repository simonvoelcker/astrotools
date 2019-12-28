import sys
import glob
import argparse
import os
import json
import math
import itertools

import numpy as np

from alignment import Alignment
from util import load_image_greyscale, save_image_greyscale
from util import get_sharpness_aog, get_sharpness_vol, get_sharpness_sobel
from skimage.transform import rescale


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
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

alignment = Alignment(args.amplification, args.threshold)

frame_offsets_by_file = dict()	# map filename to offsets tuple
frame_offsets = []

for frame_index, file in enumerate(files):
	basename = os.path.basename(file)
	frame = load_image_greyscale(file)
	offsets = alignment.get_offsets(frame, frame_index)
	
	frame_offsets_by_file[basename] = offsets
	frame_offsets.append(offsets)
	
	# frame = rescale(frame, 1.0/4.0, multichannel=False)
	# frame = (32768 * frame).astype(np.int16)
	# save_image_greyscale(frame, f'downsampled/{frame_index}.png')

	# sharpness_aog = get_sharpness_aog(frame)
	# sharpness_vol = get_sharpness_vol(frame)
	# sharpness_sobel = get_sharpness_sobel(frame)
	# brightness = np.average(frame)

	print(f'({frame_index+1}/{len(files)}) '\
		  f'Name={basename}, '\
		  f'Offset={offsets}')\
	#	  f'Sharpness(AoG)={sharpness_aog:.2f}, '\
	#	  f'Sharpness(VoL)={sharpness_vol:.10f}, '\
	#	  f'Sharpness(VoL)={sharpness_sobel:.10f}, '\
	#	  f'Brightness={brightness:.10f}')

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def distance(p1, p2):
	return math.sqrt((p2[0]-p1[0])*(p2[0]-p1[0]) + (p2[1]-p1[1])*(p2[1]-p1[1]))

distances = [distance(p1, p2) for p1, p2 in pairwise(frame_offsets)]
instability = [max(d1, d2) for d1, d2 in pairwise(distances)]

def runs(instability, thresh):
	below_thresh = [inst < thresh for inst in instability]
	# ...

print(instability)


if not args.dryrun:
	offsets_file = os.path.join(args.directory, 'offsets.json')
	with open(offsets_file, 'w') as f:
		json.dump(frame_offsets_by_file, f, indent=4, sort_keys=True)
	print('Wrote offsets.json')

	alignment.create_plot(title='Image offset distribution', filename='image_offsets.png')
	print('Wrote image_offsets.png')
