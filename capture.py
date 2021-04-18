import argparse
import numpy as np

from io import BytesIO
from astropy.io import fits

from hti.server.capture.pyindi_camera import IndiCamera

parser = argparse.ArgumentParser()
parser.add_argument('--exposure', type=float, default=0.001, help='Exposure time')
parser.add_argument('--gain', type=float, default=1000.0, help='Analog gain')
args = parser.parse_args()

####################
# Start the INDI server: indiserver indi_toupcam_ccd
####################

camera = IndiCamera()
fits_data = camera.capture_single(args.exposure, args.gain)
fits_file = BytesIO(fits_data)

with fits.open(fits_file) as fits_file:
    numpy_image = np.transpose(fits_file[0].data, (1, 2, 0))
    avg_color = np.average(numpy_image, (0, 1))
    print(avg_color)
