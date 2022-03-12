import os
import glob
import random
import time

from hti.server.capture.pyindi_camera import IndiCamera
from hti.server.capture.frame_manager import Frame
from hti.server.state.app_state import CameraState

from PIL import Image


class CameraController:
    def __init__(self):
        # auto-discover cameras
        device_names = IndiCamera.get_device_names()
        print(f"Found camera(s): {device_names}")
        self.cameras = {
            device_name: IndiCamera(device_name)
            for device_name in device_names
        }
        print("Connected to camera(s)")

    def get_device_names(self) -> list:
        return list(self.cameras.keys())

    def get_device_capabilities(self, device_name: str) -> dict:
        return self.cameras[device_name].get_capabilities()

    def capture_image(self, device_name: str, camera_state: CameraState):
        camera = self.cameras[device_name]
        fits_data = camera.capture_single(
            camera_state.exposure,
            camera_state.gain,
            camera_state.region,
        )
        return Frame(fits_data, device_name)

    def capture_sequence(self, device_name: str, camera_state: CameraState):
        camera = self.cameras[device_name]

        def run_while():
            return not camera_state.sequence_stop_requested

        for fits_data in camera.capture_sequence(
            camera_state.exposure,
            camera_state.gain,
            camera_state.region,
            run_while,
        ):
            yield Frame(fits_data, device_name)


class SimCameraController:

    def get_device_names(self):
        return [
            "Simulated capturing camera",
            "Simulated guiding camera",
        ]

    def get_device_capabilities(self, device_name: str) -> dict:
        return {
            "Simulated capturing camera": {
                "frame_width": 3000,
                "frame_height": 2000,
            },
            "Simulated guiding camera": {
                "frame_width": 2000,
                "frame_height": 1000,
            },
        }[device_name]

    def capture_image(self, device_name: str, camera_state: CameraState):
        time.sleep(camera_state.exposure)

        here = os.path.dirname(os.path.abspath(__file__))
        astro_dir = os.path.join(here, '..', '..', '..', '..')
        images_glob = os.path.join(astro_dir, 'Hall Of Fame', '*.png')
        images = glob.glob(images_glob)
        random_image_path = random.choice(images)

        frame = Frame(None, device_name)
        frame.pil_image = Image.open(random_image_path)
        frame.pil_image.load()
        return frame

    def capture_sequence(self, device_name: str, camera_state: CameraState):
        while not camera_state.sequence_stop_requested:
            yield self.capture_image(device_name, camera_state)
