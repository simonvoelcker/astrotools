import argparse
import numpy as np

from io import BytesIO
from astropy.io import fits

from hti.server.capture.pyindi_camera import IndiCamera

from lib.util import save_image_greyscale

parser = argparse.ArgumentParser()
parser.add_argument('--exposure', type=float, default=0.1, help='Exposure time')
parser.add_argument('--gain', type=float, default=1000.0, help='Analog gain')
args = parser.parse_args()

####################
# Start the INDI server: indiserver indi_toupcam_ccd (or indi_asi_ccd)
####################

camera = IndiCamera(device_name='ZWO CCD ASI178MM')  # 'Toupcam GPCMOS02000KPA'

# camera.start_stream()

fits_data = camera.capture_single(args.exposure, args.gain)
fits_file = BytesIO(fits_data)

with fits.open(fits_file) as fits_file:
    numpy_image = np.transpose(fits_file[0].data, (1, 0)) / 256  # int16 to int8
    save_image_greyscale(numpy_image, 'new_cam.jpg')

    # numpy_image = np.transpose(fits_file[0].data, (1, 2, 0))
    # avg_color = np.average(numpy_image, (0, 1))
    # print(avg_color)
