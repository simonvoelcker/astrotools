import sys
import glob
import argparse

from stacked_image import StackedImage


parser = argparse.ArgumentParser()
parser.add_argument('filename_pattern', type=str)
parser.add_argument('--offsets', type=str, default='0,0', help='Pixel-offset between first and last image. Format: <X>,<Y>')
parser.add_argument('--stride', type=int, default=1, help='Process only every Nth image')
parser.add_argument('--out', type=str, default='stacked.png', help='Output filename')
parser.add_argument('--crop', type=str, default=None, help='Crop the image to a square with center X,Y. Format: <X>,<Y>,<Radius>')

args = parser.parse_args()


files = glob.glob(args.filename_pattern)

if not files:
	print('No files')
	sys.exit(1)

print(f'Found {len(files)} files')
files.sort()

offsets = args.offsets.split(',')
x_offset = int(offsets[0])
y_offset = int(offsets[1])

image = StackedImage(files, x_offset, y_offset, args.stride)

if args.crop is not None:
	cx, cy, r = args.crop.split(',')
	image.crop(int(cx), int(cy), int(r))

image.normalize()
image.substract_pollution()
image.normalize()
image.save(args.out)
