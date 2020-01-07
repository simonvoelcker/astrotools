import os
import sys
import glob
import argparse

from analyzer import Analyzer
from frame import Frame


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--range', type=str, default=None, help='Stack only given range of images, not all')
parser.add_argument('--amplification', type=int, default=1, help='Multiply images by this number before offset detection')
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

analyzer = Analyzer(args.amplification, args.threshold)

for frame_index, filepath in enumerate(files):
	frame = Frame(filepath)
	analyzer.analyze(frame)
	print(f'Processed frame {frame_index+1}/{len(files)}: {frame.filepath}')

analyzer.write_astrometric_metadata(args.directory)
analyzer.write_offsets_file(args.directory)
analyzer.create_offsets_plot()
analyzer.write_to_influx()

print('Done')
