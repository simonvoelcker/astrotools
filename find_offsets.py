import sys
import glob
import argparse
import os
import json
import numpy as np

from PIL import Image
from stacked_image import StackedImage


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
	pil_images[0].save(filename, save_all=True, append_images=pil_images[1:], duration=100, loop=0)

def interpolate_offsets(num_images, x_offset, y_offset):
	for index in range(num_images):
		norm_index = float(index) / float(num_images-1)
		# interpolate offset
		x = round(float(x_offset) * (1.0-norm_index))
		if x_offset < 0:
			x -= x_offset
		y = round(float(y_offset) * (1.0-norm_index))
		if y_offset < 0:
			y -= y_offset
		yield x, y

def get_offset_correction(image, frame, x_ofs, y_ofs, radius):
	width, height, channels = frame.shape
	best_sim = 0
	best_corr = (0, 0)

	frame_lin = frame.flatten().astype(float)
	frame_norm = np.linalg.norm(frame_lin)
	
	for x_corr in range(-radius, radius+1):
		for y_corr in range(-radius, radius+1):

			image_slice = image[x_ofs+x_corr:x_ofs+x_corr+width, y_ofs+y_corr:y_ofs+y_corr+height, :]
			if image_slice.shape != (width, height, channels):
				print('WARN 1')
				continue

			slice_lin = image_slice.flatten().astype(float)
			num = np.dot(slice_lin, frame_lin)
			denom = np.linalg.norm(slice_lin) * frame_norm
			if denom == 0:
				print('WARN 2')
				continue

			sim = num / denom
			if sim > best_sim:
				best_sim = sim
				best_corr = x_corr, y_corr

	return best_corr


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--offsets-hint', type=str, default=None, help='Pixel-offset between first and last image. Format: <X>,<Y>')
parser.add_argument('--focus-area', type=str, default=None, help='Format: <X>,<Y>,<Radius>, in first-frame coordinates')

parser.add_argument('--out', type=str, default='stacked.png', help='Output filename')

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
	'offsets-hint': '0,0',
	'focus-area': '0,0,0',
}

# params from file override defaults
params_file = os.path.join(args.directory, 'offsets_params.json')
if os.path.isfile(params_file):
	with open(params_file, 'r') as f:
		content = json.load(f)
		params.update(content)

# params from command line override everything
if args.offsets_hint is not None:
	params.update({'offsets-hint': args.offsets_hint})
if args.focus_area is not None:
	params.update({'focus-area': args.focus_area})


print(f'Using params: {params}')

offsets_hint = params['offsets-hint'].split(',')
offset_hint_x = int(offsets_hint[0])
offset_hint_y = int(offsets_hint[1])

focus_x, focus_y, focus_r = params['focus-area'].split(',')
focus_x, focus_y, focus_r = int(focus_x), int(focus_y), int(focus_r)

image_0 = load_frame(files[0], np.int16)

frame_0 = image_0[focus_x-focus_r:focus_x+focus_r, focus_y-focus_r:focus_y+focus_r, :]
frame_width, frame_height, channels = frame_0.shape

offset_hint_x = -offset_hint_x
offset_hint_y = -offset_hint_y

image_offsets = list(interpolate_offsets(len(files), offset_hint_x, offset_hint_y))

frames = []
for index, (x,y) in enumerate(image_offsets):
	full_frame = load_frame(files[index], np.int16)

	frame = full_frame[focus_x-focus_r+x:focus_x+focus_r+x, focus_y-focus_r+y:focus_y+focus_r+y, :]

	base_offset_x = focus_x-focus_r+image_offsets[0][0]
	base_offset_y = focus_y-focus_r+image_offsets[0][1]
	max_correction = 6
	corr_x, corr_y = get_offset_correction(image_0, frame, base_offset_x, base_offset_y, max_correction)

	print(f'frame {index} has offsets {corr_x}, {corr_y}')

	frame = full_frame[focus_x-focus_r+x-corr_x:focus_x+focus_r+x-corr_x, focus_y-focus_r+y-corr_y:focus_y+focus_r+y-corr_y, :]

	if frame.shape != (frame_width, frame_height, channels):
		print(f'Discarding frame {index} because shape is bad ({frame.shape})')
		continue

	frames.append(frame)

print(f'got {len(frames)} frames now')

save_composition(frames, 'composed.png')
save_animation(frames, 'animated.gif')

# write params back to disk
#with open(params_file, 'w') as f:
#	json.dump(params, f)
