# astrotools

Python tools for astrophotography. Strongly tied to my personal setup.

Requires:
 - Python 3.6+
 - numpy and Pillow for image processing
 - skimage, simple-pid and PySerial for tracking and motor control
 - matplotlib and influxdb for analytics
 - astrometry.net image calibration CLI tools (specifically solve-field)

# the tools

## analyze.py

Performs image calibration and computation of metrics such as brightness and sharpness. Data is written to disk and InfluxDB.

## command.py

Interactive control. Can set motor speeds, target object, go-to maneuver and target tracking. Data is written to InfluxDB.

## gif.py

Creates greyscale animated gif from a directory full of images.

## serve_images.py

Serves images from a given directory, one by one, to a target directory. Used for as a mock for the actual camera.

## stack.py

Stacks a series of images into a single image. Notable features:
- Image alignment
- Darkframe correction
- Flatframe correction
- Filter shaky frames
- Auto-crop most exposed region
- Gamma correction
- RGB, Greyscale or R/G/B
