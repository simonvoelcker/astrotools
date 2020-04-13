import os
import glob
import time
import numpy as np
import datetime

from lib.indi.camera import INDICamera
from lib.indi.client import INDIClient


from PIL import Image
from astropy.io import fits


def convert_fits_image(fits_filepath, out_filepath):
    with fits.open(fits_filepath) as fits_file:
        # Useful: fits_file.info()
        numpy_image = np.transpose(fits_file[0].data, (1, 2, 0))
        pil_image = Image.fromarray(numpy_image, mode='RGB')
        pil_image.save(out_filepath)
    os.remove(fits_filepath)


class INDIController:
    _status = {'shooting': False}
    
    def __init__(self, workdir):
        self.client = INDIClient()
        self.workdir = workdir 
        if not os.path.isdir(self.workdir):
            os.makedirs(self.workdir)

    def devices(self):
        properties = self.client.get_properties()
        devices = list(set([property['device'] for property in properties]))
        result = {}
        for device in devices:
            result[device] = [p for p in properties if p['device'] == device]
        return result

    def device_names(self):
        properties = self.client.get_properties()
        devices = list(set([property['device'] for property in properties]))
        devices.sort()
        return devices

    def properties(self, device):
       return self.client.get_properties(device) 

    def property(self, device, property):
        property_element = property.split('.')
        return self.client.get_properties(device, property_element[0], property_element[1])[0]

    def set_property(self, device, property, value):
        property_element = property.split('.')
        self.client.set_property_sync(device, property_element[0], property_element[1], value)
        return self.property(device, property)

    def capture_image(self, device, exposure, gain):
        if INDIController._status['shooting']:
            raise RuntimeError('Anoter exposure is already in progress')
        imager = INDICamera(device, self.client)
        if not imager.is_camera():
            raise RuntimeError('Device {0} is not an INDI CCD Camera'.format(device))
        INDIController._status = {'shooting': True, 'exposure': exposure, 'started': time.time() }
        
        image_name = datetime.datetime.now().isoformat()
        imager.set_output(self.workdir, image_name)
        imager.shoot(exposure, gain)
        INDIController._status = {'shooting': False, 'last_exposure': exposure, 'last_ended': time.time() }

        convert_fits_image(os.path.join(self.workdir, f'{image_name}.fits'), os.path.join(self.workdir, f'{image_name}.jpg'))
        return f'{image_name}.jpg'

    def clean_cache(self):
        for file in glob(self.workdir + '/*'):
            os.remove(file)
        return len( [f for f in os.listdir(self.workdir) if os.isfile(f)] )    

    def status(self):
        status ={'now': time.time()}
        status.update(INDIController._status)
        return status
