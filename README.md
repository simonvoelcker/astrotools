# astrotools

Python tools for astro-photography. Strongly tied to my personal setup.

![M3](m3.jpg?raw=true "M3 - Globular Cluster")

## Requirements

 - Python 3.6+
 - numpy and Pillow for image processing
 - skimage, simple-pid and PySerial for tracking and motor control
 - matplotlib and influxdb for analytics
 - astrometry.net image calibration CLI tools (specifically solve-field)
 - astropy for FITS files

Dockerization is planned and will happen on a cloudy day.

# the tools

## HTI - Human Telescope Interface

This is a web application with a rich set of features for controlling a telescope and capturing image data. It is build with Flask and React and is best run on a desktop machine.

Notable features and integrations:
- Images are captured via INDI
- Mount is controlled via serial port (interfaces with Arduino to control stepper motors)
- Current celestial coordinates are computed using the Astrometry CLI
- An SQLite database is used to store a target catalog (e.g. NGC objects)
- Guiding is done via a control loop featuring a PID controller for each axis

The HTI is ever-evolving, and may not be very useful to others as a whole just yet.

## CLI tools

### analyze.py

Performs image calibration and computation of metrics such as brightness and sharpness. Data is written to disk and InfluxDB.

### stack.py

Stacks a series of images into a single image. Notable features:
- Image alignment
- Darkframe correction
- Flatframe correction
- Filter shaky frames
- Auto-crop most exposed region
- Gamma correction
- RGB, Greyscale or R/G/B
