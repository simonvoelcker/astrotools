import os
import numpy as np
import datetime
import glob
import random
import time

from .camera import INDICamera
from .client import INDIClient


from PIL import Image
from astropy.io import fits


def convert_fits_image(fits_filepath, out_filepath):
    if not os.path.isdir(os.path.dirname(out_filepath)):
        os.makedirs(os.path.dirname(out_filepath))
    with fits.open(fits_filepath) as fits_file:
        # Useful: fits_file.info()
        numpy_image = np.transpose(fits_file[0].data, (1, 2, 0))
        pil_image = Image.fromarray(numpy_image, mode='RGB')
        pil_image.save(out_filepath)
    os.remove(fits_filepath)


class INDIController:
    def __init__(self, static_dir):
        self.client = INDIClient()
        self.cameras = dict()  # by device name
        self.static_dir = static_dir
        self.shooting = False

        if not os.path.isdir(self.static_dir):
            os.makedirs(self.static_dir)

    def devices(self):
        properties = self.client.get_properties()
        devices = list(set([property['device'] for property in properties]))
        result = {}
        for device in devices:
            result[device] = [p for p in properties if p['device'] == device]
        return result

    def properties(self, device):
        return self.client.get_properties(device)

    def property(self, device, property):
        property_element = property.split('.')
        return self.client.get_properties(device, property_element[0], property_element[1])[0]

    def set_property(self, device, property, value):
        property_element = property.split('.')
        self.client.set_property_sync(device, property_element[0], property_element[1], value)
        return self.property(device, property)

    def get_camera(self, device_name):
        if device_name not in self.cameras:
            camera = INDICamera(device_name, self.client)
            camera.connect()
            if not camera.is_camera():
                raise RuntimeError(f'Device {device_name} is not an INDI CCD Camera')
            self.cameras[device_name] = camera
        return self.cameras[device_name]

    def capture_image(self, device_name, frame_type, exposure, gain):
        if self.shooting:
            raise RuntimeError('Another exposure is already in progress')

        self.shooting = True

        today = datetime.date.today().isoformat()
        path_prefix = os.path.join(today, frame_type)
        image_name = datetime.datetime.now().isoformat()
        camera = self.get_camera(device_name)
        camera.set_output(self.static_dir, image_name)
        camera.shoot(exposure, gain)

        self.shooting = False

        convert_fits_image(fits_filepath=os.path.join(self.static_dir, f'{image_name}.fits'),
                           out_filepath=os.path.join(self.static_dir, path_prefix, f'{image_name}.png'))

        return f'{path_prefix}/{image_name}.png'


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