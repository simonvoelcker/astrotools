import argparse

from lib.indi.pyindi_camera import IndiCamera

parser = argparse.ArgumentParser()
parser.add_argument('--exposure', type=float, default=0.1, help='Exposure time')
parser.add_argument('--gain', type=float, default=1000.0, help='Analog gain')
parser.add_argument('--out', type=str, default='./capture.png', help='Output file path')
args = parser.parse_args()

####################
# Start the INDI server: indiserver indi_toupcam_ccd
####################

camera = IndiCamera()
camera.capture_single(args.exposure, args.gain, filepath=args.out)

print(f'Wrote {args.out}')
