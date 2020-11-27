import PyIndi
import time
import sys
import queue
import io
import os

import numpy as np
from PIL import Image
from astropy.io import fits


class IndiClient(PyIndi.BaseClient):
    def __init__(self, host, port):
        super(IndiClient, self).__init__()
        self.event_queue = None
        # connect
        self.setServer(host, port)
        if not (self.connectServer()):
            print(f'Server not running: {host}:{port}')
            sys.exit(1)

    def subscribe(self):
        self.event_queue = queue.Queue()
        return self.event_queue

    def newDevice(self, d):
        pass

    def newProperty(self, p):
        pass

    def removeProperty(self, p):
        pass

    def newBLOB(self, bp):
        if self.event_queue is not None:
            self.event_queue.put(bp)

    def newSwitch(self, svp):
        pass

    def newNumber(self, nvp):
        pass

    def newText(self, tvp):
        pass

    def newLight(self, lvp):
        pass

    def newMessage(self, d, m):
        pass

    def serverConnected(self):
        pass

    def serverDisconnected(self, code):
        pass


def get_retry(get_function, delay=0.5):
    while True:
        val = get_function()
        if val:
            return val
        time.sleep(delay)


class IndiCamera:

    def __init__(self, device_name='Toupcam GPCMOS02000KPA'):
        self.indi_client = IndiClient('localhost', 7624)
        self.blob_event_queue = self.indi_client.subscribe()

        self.device_ccd = get_retry(lambda: self.indi_client.getDevice(device_name))
        self.ccd_connect = get_retry(lambda: self.device_ccd.getSwitch("CONNECTION"))

        if not self.device_ccd.isConnected():
            self.ccd_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            self.ccd_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            self.indi_client.sendNewSwitch(self.ccd_connect)

        self.ccd_exposure = get_retry(lambda: self.device_ccd.getNumber("CCD_EXPOSURE"))

        self.ccd_active_devices = get_retry(lambda: self.device_ccd.getText("ACTIVE_DEVICES"))
        self.ccd_active_devices[0].text = "Camera"
        self.indi_client.sendNewText(self.ccd_active_devices)

        # inform the indi server that we want to receive the "CCD1" blob
        self.indi_client.setBLOBMode(PyIndi.B_ALSO, device_name, "CCD1")

        self.ccd_ccd1 = get_retry(lambda: self.device_ccd.getBLOB("CCD1"))

    def save_image(self, out_filepath):
        blob = self.ccd_ccd1[0]
        fits_data = blob.getblobdata()
        fits_file = io.BytesIO(fits_data)
        with fits.open(fits_file) as fits_file:
            # Useful: fits_file.info()
            numpy_image = np.transpose(fits_file[0].data, (1, 2, 0))
            pil_image = Image.fromarray(numpy_image, mode='RGB')
            pil_image.save(out_filepath)

    def capture_single(self, exposure, out_filepath):
        self.ccd_exposure[0].value = exposure
        self.indi_client.sendNewNumber(self.ccd_exposure)

        # could use the event that comes out of this somehow
        self.blob_event_queue.get()
        self.save_image(out_filepath)

    def capture_sequence(self, exposure, out_directory):

        self.ccd_exposure[0].value = exposure
        self.indi_client.sendNewNumber(self.ccd_exposure)

        i = 0
        while True:
            # wait for the ith exposure
            self.blob_event_queue.get()

            # we can start immediately the next one
            self.ccd_exposure[0].value = exposure
            self.indi_client.sendNewNumber(self.ccd_exposure)

            # and meanwhile process the received one
            filepath = os.path.join(out_directory, f'frame_{i:04}.png')
            self.save_image(filepath)
            i += 1


cam = IndiCamera()
cam.capture_sequence(1, '/home/simon/Hobby/astro/beute2')
