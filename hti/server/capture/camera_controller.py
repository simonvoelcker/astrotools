import os
import glob
import random
import time

from .pyindi_camera import IndiCamera
from .frame_manager import Frame

from PIL import Image


class CameraController:
    def __init__(self):
        self.camera = None

    def get_camera(self):
        if self.camera is None:
            self.camera = IndiCamera()
        return self.camera

    def capture_image(self, frame_type, exposure, gain):
        fits_data = self.get_camera().capture_single(exposure, gain)
        return Frame(fits_data, frame_type)

    def capture_sequence(self, frame_type, exposure, gain, run_while=None):
        for fits_data in self.get_camera().capture_sequence(exposure, gain, run_while):
            yield Frame(fits_data, frame_type)


class SimCameraController:
    def capture_image(self, frame_type, exposure, gain):
        time.sleep(exposure)

        here = os.path.dirname(os.path.abspath(__file__))
        astro_dir = os.path.join(here, '..', '..', '..', '..')
        images_glob = os.path.join(astro_dir, 'NGC 891 - Galaxy', '2020-11-14', '**', '*.png')
        images = glob.glob(images_glob)
        random_image_path = random.choice(images)

        frame = Frame(fits_data=None, frame_type=frame_type)
        frame.pil_image = Image.open(random_image_path)
        frame.pil_image.load()
        return frame

    def capture_sequence(self, frame_type, exposure, gain, run_while=None):
        while True:
            yield self.capture_image(frame_type, exposure, gain)
            if run_while is not None and not run_while():
                break
