import argparse
import glob
import os
import sys

from lib.analyzer import Analyzer
from lib.calibration_analyzer import CalibrationAnalyzer
from lib.frame_quality_analyzer import FrameQualityAnalyzer
from lib.offset_analyzer import OffsetAnalyzer

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

analyzer = Analyzer(analyzers=[
	OffsetAnalyzer(
		args.sigma_clip,
		os.path.join(args.directory, 'offsets.json'),
		os.path.join('out', 'offsets_plot.png'),
	),
	CalibrationAnalyzer(
		os.path.join(args.directory, 'calibration_data.json'),
	),
	FrameQualityAnalyzer()
])

print('Starting analysis')
analyzer.analyze(files)
print('Writing results')
analyzer.write_results()
print('Writing to InfluxDB')
analyzer.write_to_influx()
print('Done')
