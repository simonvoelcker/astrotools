import os
import sys
import glob
import argparse
import numpy as np

from skimage.transform import resize
from PIL import Image


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--range', type=str, default=None, help='Stack only given range of images, not all')
parser.add_argument('--downscale', type=int, default=1, help='Scale down images by this factor')
parser.add_argument('--fps', type=int, default=10, help='Frames per second')

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

images = []
for filepath in files:
	image = Image.open(filepath).convert('L')
	image = image.resize((
		int(image.width/args.downscale),
		int(image.height/args.downscale),
	))
	images.append(image)	

delay_ms = int(1000.0 / args.fps)
images[0].save('animation.gif', save_all=True, append_images=images[1:], duration=delay_ms, loop=0)

print('Done')
