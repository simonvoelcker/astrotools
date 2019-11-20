import sys
import glob
import argparse
import os
import json
import math
import numpy as np

from PIL import Image

from skimage.feature import register_translation

import matplotlib.pyplot as plt


def load_frame_for_offset_detection(filename, amplification, threshold):
	pil_image = Image.open(filename).convert('L')
	yx_image = np.asarray(pil_image, dtype=np.int16)
	xy_image = np.transpose(yx_image, (1, 0))
	xy_image = np.clip(xy_image * amplification, threshold, 255)
	return xy_image


def save_image(image, filename):
	yxc_image = np.transpose(image, (1, 0, 2))
	yxc_image = yxc_image.astype(np.int8)
	pil_image = Image.fromarray(yxc_image, mode='RGB')
	pil_image.save(filename)


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--max-frame-distance', type=int, default=480, help='Maximum cartesian distance between frames, in pixels')
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
	print(f'Only {len(files)} files selected for offset detection')

key_frame = load_frame_for_offset_detection(files[0], args.amplification, args.threshold)
key_frame_index = 0
prev_frame = None

if False:
	color_frame = np.zeros((key_frame.shape[0], key_frame.shape[1], 3), dtype=np.int16)
	for c in range(3):
		color_frame[:,:,c] = key_frame
	save_image(color_frame, 'stretched.png')
	sys.exit(0)

frame_offsets = {0: (0,0)}	# map frame index to offsets-tuple
frame_offsets_by_file = dict()

for frame_index, file in enumerate(files):
	curr_frame = load_frame_for_offset_detection(file, args.amplification, args.threshold)

	(offset_x, offset_y), error, _ = register_translation(key_frame, curr_frame)
	cartesian_offset = math.sqrt(offset_x*offset_x + offset_y*offset_y)
	print(f'Frame {frame_index}: Got offsets x={offset_x}, y={offset_y}, total={cartesian_offset:.2f}, error={error:.2f}')
	
	if cartesian_offset > args.max_frame_distance:
		if key_frame_index == frame_index-1:
			print('Too big offset between adjacent frames. Aborting.')
			sys.exit(1)

		print(f'That was too far. Using frame {frame_index-1} as key new frame.')
		key_frame = prev_frame
		key_frame_index = frame_index-1

		(offset_x, offset_y), error, _ = register_translation(key_frame, curr_frame)
		cartesian_offset = math.sqrt(offset_x*offset_x + offset_y*offset_y)
		print(f'Frame {frame_index}: Got offsets x={offset_x}, y={offset_y}, total={cartesian_offset:.2f}, error={error:.2f}')

	key_frame_offset = frame_offsets[key_frame_index]
	offset_x += key_frame_offset[0]
	offset_y += key_frame_offset[1]

	frame_offsets[frame_index] = (offset_x, offset_y)
	frame_offsets_by_file[os.path.basename(file)] = (offset_x, offset_y)
	prev_frame = curr_frame

# write offsets files
offsets_file = os.path.join(args.directory, 'offsets.json')
with open(offsets_file, 'w') as f:
	json.dump(frame_offsets_by_file, f, indent=4, sort_keys=True)


x_offsets = np.array([x for _, (x,y) in frame_offsets.items()])
y_offsets = np.array([y for _, (x,y) in frame_offsets.items()])

colors = (0,0,0)
area = np.pi*3

# Plot
plt.scatter(x_offsets, y_offsets, s=area, c=colors, alpha=0.5)
plt.title('Image offset distribution')
plt.xlabel('x')
plt.ylabel('y')
plt.savefig('image_offsets.png')