import sys
import glob
import argparse
import os
import json
import numpy as np

from PIL import Image
from stacked_image import StackedImage

from skimage.feature import register_translation


def load_frame(filename, dtype):
	pil_image = Image.open(filename)
	yxc_image = np.asarray(pil_image, dtype=dtype)
	xyc_image = np.transpose(yxc_image, (1, 0, 2))
	return xyc_image

def save_composition(frames, filename, dtype=np.int8):
	frames_per_axis = 1+int(len(frames)**0.5)

	composed_image = np.zeros((frame_width*frames_per_axis, frame_height*frames_per_axis, channels), dtype=dtype)
	for index, frame in enumerate(frames):
		x = index % frames_per_axis
		y = index // frames_per_axis
		composed_image[x*frame_width:(x+1)*frame_width, y*frame_height:(y+1)*frame_height, :] = frame

	yxc_image = np.transpose(composed_image, (1, 0, 2))
	yxc_image = yxc_image.astype(dtype)
	pil_image = Image.fromarray(yxc_image, mode='RGB')
	pil_image.save(filename)

def save_animation(frames, filename, dtype=np.int8):
	# (1) need to pick R channel and store as greyscale
	pil_images = []
	for index, frame in enumerate(frames):
		yxc_image = np.transpose(frame, (1, 0, 2))
		yxc_image = yxc_image.astype(np.int8)[:,:,0]
		pil_image = Image.fromarray(yxc_image, mode='L')
		pil_images.append(pil_image)	
	pil_images[0].save(filename, save_all=True, append_images=pil_images[1:], duration=50, loop=0)

parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--out', type=str, default='animation.gif', help='Output filename')

args = parser.parse_args()

search_pattern = os.path.join(args.directory, args.filename_pattern)
files = glob.glob(search_pattern)

if not files:
	print('No files. Use --filename-pattern if the images are not .tif')
	sys.exit(1)

print(f'Found {len(files)} files')
files.sort()

frame_0 = load_frame(files[0], np.int16)
frame_width, frame_height, channels = frame_0.shape

frames = []
frame_offsets = {}	# map filename to offsets-tuple

for index, file in enumerate(files):
	frame = load_frame(file, np.int16)

	offset, error, diffphase = register_translation(frame_0[:,:,0], frame[:,:,0])
	offset_x, offset_y = offset

	print(f'Frame {index}: Got offsets {offset_x}, {offset_y}, error={error}, diffphase={diffphase}')

	# roll image, effectively stabilizing the frame_0 situation
	frame = np.roll(frame, int(offset_x), axis=0)
	frame = np.roll(frame, int(offset_y), axis=1)

	if frame.shape != (frame_width, frame_height, channels):
		print(f'Discarding frame {index} because shape is bad (found {frame.shape} expected {(frame_width, frame_height)}))')
		continue

	frames.append(frame)
	file_basename = os.path.basename(file)
	frame_offsets[file_basename] = (offset_x, offset_y)

print(f'got {len(frames)} frames now')

save_animation(frames, args.out)

# write offsets files
offsets_file = os.path.join(args.directory, 'offsets.json')
with open(offsets_file, 'w') as f:
	json.dump(frame_offsets, f, indent=4, sort_keys=True)
