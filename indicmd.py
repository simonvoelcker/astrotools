import argparse
import os
import datetime
import numpy

from lib.indi.client import INDIClient
from lib.indi.camera import INDICamera

from PIL import Image
from astropy.io import fits


def convert_fits_image(fits_filepath, out_filepath):
	with fits.open(fits_filepath) as fits_file:
		fits_file.info()
		numpy_image = numpy.transpose(fits_file[0].data, (1, 2, 0))
		pil_image = Image.fromarray(numpy_image, mode='RGB')
		pil_image.save(out_filepath)
	os.remove(fits_filepath)


parser = argparse.ArgumentParser()
parser.add_argument('--exposure', type=float, default=1.0, help='Exposure time')
args = parser.parse_args()

####################
# Start the INDI server: indiserver indi_toupcam_ccd
####################

client = INDIClient()
camera = INDICamera('Toupcam GPCMOS02000KPA', client)
camera.connect()

# cause some action on the line
# camera.properties()

# print('Camera properties:')
# for prop in camera.properties():
# 	print(f'{prop["device"]}.{prop["property"]}.{prop["element"]}={prop["value"]}')

workdir = '/home/simon/Hobby/astro/astrotools/in'
fits_path = os.path.join(workdir, 'fits')
png_path = os.path.join(workdir, 'png')
basename = datetime.datetime.now().isoformat()

camera.set_output(path=fits_path, prefix=basename)
camera.shoot(exposure=args.exposure)
camera.disconnect()

convert_fits_image(os.path.join(fits_path, f'{basename}.fits'), os.path.join(png_path, f'{basename}.png'))
