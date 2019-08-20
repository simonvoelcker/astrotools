import sys
import glob
import argparse
import os
import json
import math
import numpy as np

from PIL import Image

from skimage.feature import register_translation


def load_frame(filename, dtype):
	pil_image = Image.open(filename)
	yxc_image = np.asarray(pil_image, dtype=dtype)
	xyc_image = np.transpose(yxc_image, (1, 0, 2))
	return xyc_image

parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--max-frame-distance', type=int, default=480, help='Maximum cartesian distance between frames, in pixels')

args = parser.parse_args()

search_pattern = os.path.join(args.directory, args.filename_pattern)
files = glob.glob(search_pattern)

if not files:
	print('No files. Use --filename-pattern if the images are not .tif')
	sys.exit(1)

print(f'Found {len(files)} files')
files.sort()

start_frame = 0
end_frame = 1000

key_frame = load_frame(files[start_frame], np.int8)
key_frame_index = 0
prev_frame = None

frame_offsets = {0: (0,0)}	# map frame index to offsets-tuple
frame_offsets_by_file = dict()

for frame_index, file in enumerate(files[start_frame:end_frame]):
	curr_frame = load_frame(file, np.int8)

	(offset_x, offset_y), error, _ = register_translation(key_frame[:,:,0], curr_frame[:,:,0])
	cartesian_offset = math.sqrt(offset_x*offset_x + offset_y*offset_y)
	print(f'Frame {frame_index}: Got offsets x={offset_x}, y={offset_y}, total={cartesian_offset:.2f}, error={error:.2f}')
	
	if cartesian_offset > args.max_frame_distance:
		if key_frame_index == frame_index-1:
			print('Too big offset between adjacent frames. Aborting.')
			sys.exit(1)

		print(f'That was too far. Using frame {frame_index-1} as key new frame.')
		key_frame = prev_frame
		key_frame_index = frame_index-1

		(offset_x, offset_y), error, _ = register_translation(key_frame[:,:,0], curr_frame[:,:,0])
		cartesian_offset = math.sqrt(offset_x*offset_x + offset_y*offset_y)
		print(f'Frame {frame_index}: Got offsets x={offset_x}, y={offset_y}, total={cartesian_offset:.2f}, error={error:.2f}')

	key_frame_offset = frame_offsets[key_frame_index]
	offset_x += key_frame_offset[0]
	offset_y += key_frame_offset[1]

	frame_offsets[frame_index] = (offset_x, offset_y)
	frame_offsets_by_file[file] = (offset_x, offset_y)
	prev_frame = curr_frame

# write offsets files
offsets_file = os.path.join(args.directory, 'offsets.json')
with open(offsets_file, 'w') as f:
	json.dump(frame_offsets, f, indent=4, sort_keys=True)
