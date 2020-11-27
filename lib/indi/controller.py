import os
import datetime
import glob
import random
import time


from .pyindi_camera import IndiCamera


from PIL import Image


class INDIController:
    def __init__(self, static_dir):
        self.cameras = dict()  # by device name
        self.static_dir = static_dir
        self.shooting = False

        if not os.path.isdir(self.static_dir):
            os.makedirs(self.static_dir)

    def get_camera(self, device_name):
        if device_name not in self.cameras:
            camera = IndiCamera()
            self.cameras[device_name] = camera
        return self.cameras[device_name]

    def capture_image(self, device_name, frame_type, exposure, gain):
        if self.shooting:
            raise RuntimeError('Another exposure is already in progress')

        self.shooting = True

        today = datetime.date.today().isoformat()
        path_prefix = os.path.join(today, frame_type)
        image_name = f'{datetime.datetime.now().isoformat()}.png'

        out_dir = os.path.join(self.static_dir, path_prefix)
        os.makedirs(out_dir, exist_ok=True)

        camera = self.get_camera(device_name)
        camera.capture_single(exposure, gain, out_dir, image_name)

        self.shooting = False

        return os.path.join(path_prefix, image_name)


class INDIControllerMock:
    def __init__(self, static_dir):
        self.static_dir = static_dir

    def devices(self):
        return {"Toupcam GPCMOS02000KPA": []}

    def properties(self, device):
        raise NotImplementedError

    def property(self, device, property):
        raise NotImplementedError

    def set_property(self, device, property, value):
        raise NotImplementedError

    def capture_image(self, device_name, frame_type, exposure, gain):
        time.sleep(exposure)

        today = datetime.date.today().isoformat()
        path_prefix = os.path.join(today, frame_type)

        here = os.path.dirname(os.path.abspath(__file__))
        astro_dir_glob = os.path.join(here, '..', '..', '..', 'NGC*', '**', '*.tif')
        images = glob.glob(astro_dir_glob)
        random_image_path = random.choice(images)
        out_dir = os.path.join(self.static_dir, path_prefix)
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        # convert to jpg while copying to static/path_prefix
        filename, extension = os.path.splitext(os.path.basename(random_image_path))
        out_filepath = os.path.join(self.static_dir, path_prefix, f'{filename}.jpg')
        Image.open(random_image_path).save(out_filepath)

        return os.path.join(path_prefix, f'{filename}.jpg')
