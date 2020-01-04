import sys
import glob
import argparse
import os
import json
import math
import itertools

import numpy as np

from alignment import Alignment
from util import get_astrometric_metadata, load_image_greyscale


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--range', type=str, default=None, help='Stack only given range of images, not all')
parser.add_argument('--amplification', type=int, default=5, help='Multiply images by this number before offset detection')
parser.add_argument('--threshold', type=int, default=128, help='Clip images by this brightness value after amplification')

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
	print(f'Only {len(files)} files selected')

alignment = Alignment(args.amplification, args.threshold)

frame_offsets_by_file = dict()	# map filename to offsets tuple
astrometric_metadata_by_file = dict()

for frame_index, file in enumerate(files):
	basename = os.path.basename(file)
	astrometric_metadata_by_file[basename] = get_astrometric_metadata(file)

	frame = load_image_greyscale(file)
	offsets = alignment.get_offsets(frame, frame_index)
	frame_offsets_by_file[basename] = offsets
	
	print(f'({frame_index+1}/{len(files)}) Name={basename}, Offset={offsets}')

astrometric_metadata_file = os.path.join(args.directory, 'astrometric_metadata.json')
with open(astrometric_metadata_file, 'w') as f:
	json.dump(astrometric_metadata_by_file, f, indent=4, sort_keys=True)

offsets_file = os.path.join(args.directory, 'offsets.json')
with open(offsets_file, 'w') as f:
	json.dump(frame_offsets_by_file, f, indent=4, sort_keys=True)

# alignment.create_plot(title='Image offset distribution', filename='image_offsets.png')
print('Done')

#
# Experimental: Detect blurry frames through offsets between runs of three frames
#
# def pairwise(iterable):
#     "s -> (s0,s1), (s1,s2), (s2, s3), ..."
#     a, b = itertools.tee(iterable)
#     next(b, None)
#     return zip(a, b)
# 
# def distance(p1, p2):
# 	return math.sqrt((p2[0]-p1[0])*(p2[0]-p1[0]) + (p2[1]-p1[1])*(p2[1]-p1[1]))
# 
# distances = [distance(p1, p2) for p1, p2 in pairwise(frame_offsets)]
# instability = [max(d1, d2) for d1, d2 in pairwise(distances)]
# 
# def runs(instability, thresh):
# 	below_thresh = [inst < thresh for inst in instability]
# 	# ...
# 
# print(instability)
# 