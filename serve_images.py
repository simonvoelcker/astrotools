import sys
import glob
import argparse
import os
import time
import shutil


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('--filename-pattern', type=str, default='*.tif', help='Pattern to use when searching for input images')
parser.add_argument('--out-directory', type=str, help='Output directory')
parser.add_argument('--delay', type=int, default=3, help='Delay between images, in seconds')

args = parser.parse_args()

search_pattern = os.path.join(args.directory, args.filename_pattern)
files = glob.glob(search_pattern)

if not files:
	print('No files. Use --filename-pattern if the images are not .tif')
	sys.exit(1)

print(f'Found {len(files)} files')
files.sort()

for index, file in enumerate(files):
	print(f'Serving file {index}')
	shutil.copy(file, args.out_directory)
	time.sleep(args.delay)

print('Done')
