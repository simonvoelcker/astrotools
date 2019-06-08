import sys
import glob
import numpy as np

from util import save_image
from stacked_image import StackedImage


if __name__ == '__main__':
	if len(sys.argv) not in (3,4):
		print(f'Usage: {sys.argv[0]} <filename_pattern> <total_offset(x,y)> <stride=1>')
		sys.exit(1)

	filename_pattern = sys.argv[1]
	files = glob.glob(filename_pattern)
	files.sort()

	if not files:
		print('No files')
		sys.exit(1)

	stride = int(sys.argv[3]) if len(sys.argv) == 4 else 1 
	print(f'{len(files)} files, stride={stride}')

	offsets = sys.argv[2].split(',')
	x_offset = int(offsets[0])
	y_offset = int(offsets[1])

	image = StackedImage(files, x_offset, y_offset, stride)

	#cx, cy, r = 2583, 934, 400
	#image = image[cx-r:cx+r, cy-r:cy+r, :]
	#samples = samples[cx-r:cx+r, cy-r:cy+r]
	
	image.normalize()
	image.substract_pollution()
	image.normalize()
	
	image_int = (255.0 * image.image).astype(np.int16)

	save_image(image_int, 'stacked.png', rgb_mode=True)
