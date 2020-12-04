import os
import glob
import random
import time


from lib.indi.pyindi_camera import IndiCamera
from .frame_manager import Frame

from PIL import Image


class CameraController:
    def __init__(self):
        self.cameras = dict()  # by device name

    def get_camera(self, device_name):
        if device_name not in self.cameras:
            camera = IndiCamera()
            self.cameras[device_name] = camera
        return self.cameras[device_name]

    def capture_image(self, device_name, frame_type, exposure, gain):
        camera = self.get_camera(device_name)
        fits_data = camera.capture_single(exposure, gain)
        return Frame(fits_data, frame_type)

    def capture_sequence(self, device_name, frame_type, exposure, gain, run_callback=None):
        camera = self.get_camera(device_name)
        for fits_data in camera.capture_sequence(exposure, gain, run_callback=run_callback):
            yield Frame(fits_data, frame_type)


class SimCameraController:
    def capture_image(self, device_name, frame_type, exposure, gain):
        time.sleep(exposure)

        here = os.path.dirname(os.path.abspath(__file__))
        astro_dir_glob = os.path.join(here, '..', '..', '..', 'NGC*', '**', '*.png')
        images = glob.glob(astro_dir_glob)
        random_image_path = random.choice(images)

        frame = Frame(fits_data=None, frame_type=frame_type)
        frame.pil_image = Image.open(random_image_path)
        frame.pil_image.load()
        return frame
