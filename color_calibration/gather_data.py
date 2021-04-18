import csv
import random
import numpy as np

from io import BytesIO
from astropy.io import fits
from tkinter import Tk

from hti.server.capture.pyindi_camera import IndiCamera


class App(Tk):
    def __init__(self, size, delay, exposure, gain, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.camera = IndiCamera()
        self.geometry(f'{size}x{size}')
        self.delay = delay
        self.exposure = exposure
        self.gain = gain

        self.write_header()
        self.update_color()

    def update_color(self):
        color = random.randint(0, 0xFFFFFF)
        color_str = "#%06x" % color
        self.title(color_str)
        self.config(bg=color_str)

        color_array = [
            float((color & 0xFF0000) >> 16),
            float((color & 0xFF00) >> 8),
            float(color & 0xFF),
        ]
        self.after(self.delay, lambda: self.take_sample(real_color=color_array))

    def take_sample(self, real_color):
        fits_data = self.camera.capture_single(self.exposure, self.gain)
        fits_file = BytesIO(fits_data)

        with fits.open(fits_file) as fits_file:
            numpy_image = np.transpose(fits_file[0].data, (1, 2, 0))
            measured_color = np.average(numpy_image, (0, 1)).tolist()
            self.write_sample(real_color, measured_color, self.exposure, self.gain)
            print(int(np.average(real_color)), int(np.average(measured_color)))

        self.after(self.delay, lambda: self.update_color())

    @staticmethod
    def write_header():
        with open('samples.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                "exposure", "gain", "xr", "xg", "xb", "yr", "yg", "yb",
            ])

    @staticmethod
    def write_sample(real_color, measured_color, exposure, gain):
        with open('samples.csv', 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([exposure, gain] + real_color + measured_color)


app = App(size=800, delay=250, exposure=0.003, gain=20000.0)
app.mainloop()
