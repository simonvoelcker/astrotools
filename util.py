import numpy as np
import subprocess
import re
import os
import glob

from PIL import Image
from skimage.filters import laplace, sobel
from coordinates import Coordinates
from image_stack_nebula import ImageStackNebula
from influxdb import InfluxDBClient


def load_image(filename, dtype=np.int16):
	pil_image = Image.open(filename)
	yxc_image = np.asarray(pil_image, dtype=dtype)
	xyc_image = np.transpose(yxc_image, (1, 0, 2))
	return xyc_image


def load_image_greyscale(filename, dtype=np.int16):
	pil_image = Image.open(filename).convert('L')
	yx_image = np.asarray(pil_image, dtype=dtype)
	xy_image = np.transpose(yx_image, (1, 0))
	return xy_image


def create_average_frame(directory, search_pattern, color_mode):
	if directory is None:
		return None
	full_search_pattern = os.path.join(directory, search_pattern)
	files = glob.glob(full_search_pattern)
	print(f'Found {len(files)} frames in {directory} - Creating an average frame')
	average_frame = ImageStackNebula.create_average_frame(directory, files, color_mode)
	return average_frame


def save_image(image, filename):
	yxc_image = np.transpose(image, (1, 0, 2))
	yxc_image = yxc_image.astype(np.int8)
	pil_image = Image.fromarray(yxc_image, mode='RGB')
	pil_image.save(filename)


def save_image_greyscale(image, filename):
	yx_image = np.transpose(image, (1, 0))
	yx_image = yx_image.astype(np.int8)
	# convert to RGB, ghetto style
	yxc_image = np.zeros((yx_image.shape[0], yx_image.shape[1], 3), dtype=np.int8)
	yxc_image[:,:,0] = yx_image
	yxc_image[:,:,1] = yx_image
	yxc_image[:,:,2] = yx_image
	pil_image = Image.fromarray(yxc_image, mode='RGB')
	pil_image.save(filename)


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

def get_sharpness_aog(frame):
	# average of gradient
	gy, gx = np.gradient(frame)
	gnorm = np.sqrt(gx**2 + gy**2)
	return np.average(gnorm)

def get_sharpness_vol(frame):
	# variance of laplacian on a downscaled image
	return laplace(frame).var()

def get_sharpness_sobel(frame):
	# variance of sobel
	return sobel(frame).var()

def locate_image(filepath, cpulimit=5):
	solve_command = [
		'/usr/local/astrometry/bin/solve-field',
		filepath,
		'--scale-units', 'arcsecperpix',
		'--scale-low', '0.8',
		'--scale-high', '1.0',
		'--cpulimit', str(cpulimit),
		'--overwrite',
		'--no-plots',
		'--parity', 'pos',
		'--temp-axy',
		'--solved', 'none',
		'--corr', 'none',
		'--new-fits', 'none',
		'--index-xyls', 'none',
		'--match', 'none',
		'--rdls', 'none',
		'--wcs', 'none',
	]
	try:
		output = subprocess.check_output(solve_command, timeout=cpulimit, stderr=subprocess.DEVNULL).decode()
	except subprocess.TimeoutExpired:
		print('Timed out trying to solve field')
		return None
	astrometry_coordinates_rx = re.compile(r'^.*RA,Dec = \((?P<ra>[\d\.]+),(?P<dec>[\d\.]+)\).*$', re.DOTALL)
	match = astrometry_coordinates_rx.match(output)
	if not match:
		return None
	return Coordinates(float(match.group('ra')), float(match.group('dec')))


def query_offsets(path_prefix):
	# WIP and maybe a bad idea.
	# should keep tracking and alignment cleanly separated, in prep for a guiding camera.

	# Usage: query_offsets('../beute/191013')
	path_prefix = path_prefix.replace('/', '\\/')
	influx_client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='tracking')
	offsets_query = f'SELECT ra_image_error, dec_image_error, file_path '\
					f'FROM axis_log WHERE file_path =~ /{path_prefix}*/ ORDER BY time ASC'

	offsets_result = influx_client.query(offsets_query)
	# it will remain influxDBs secret why this is so complicated
	rows = offsets_result.items()[0][1]
	return {row['file_path']: (row['ra_image_error'], row['dec_image_error']) for row in rows}
