import argparse
import glob
import os
import sys

from lib.analyzer import Analyzer


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.png', help='Pattern to use when searching for input images')
parser.add_argument('--range', type=str, default=None, help='Stack only given range of images, not all')
parser.add_argument('--sigma-clip', type=int, default=None, help='Apply sigma clipping with given sigma before offset detection')

args = parser.parse_args()

search_pattern = os.path.join(args.directory, args.filename_pattern)
files = glob.glob(search_pattern)

if not files:
	print('No files. Use --filename-pattern if the images are not .png')
	sys.exit(1)

print(f'Found {len(files)} files')
files.sort()

if args.range is not None:
	image_range = args.range.split(',')
	files = files[int(image_range[0]):int(image_range[1])]
	print(f'Only {len(files)} files selected')

analyzer = Analyzer(args.sigma_clip)
analyzer.analyze(files)
analyzer.write_calibration_data(args.directory)
analyzer.write_offsets_file(args.directory)
analyzer.create_offsets_plot('out/offsets_plot.png')
analyzer.write_to_influx()

print('Done')
