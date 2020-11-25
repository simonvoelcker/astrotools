import PyIndi
import time
import sys
import queue


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


class IndiCamera:
    def __init__(self, device_name='Toupcam GPCMOS02000KPA'):
        # connect the server
        self.indi_client = IndiClient('localhost', 7624)
        self.blob_event_queue = self.indi_client.subscribe()

        self.device_ccd = self.indi_client.getDevice(device_name)
        while not self.device_ccd:
            time.sleep(0.5)
            self.device_ccd = self.indi_client.getDevice(device_name)

        ccd_connect = self.device_ccd.getSwitch("CONNECTION")
        while not ccd_connect:
            time.sleep(0.5)
            ccd_connect = self.device_ccd.getSwitch("CONNECTION")

        if not self.device_ccd.isConnected():
            ccd_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            ccd_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            self.indi_client.sendNewSwitch(ccd_connect)

        self.ccd_exposure = self.device_ccd.getNumber("CCD_EXPOSURE")
        while not self.ccd_exposure:
            time.sleep(0.5)
            self.ccd_exposure = self.device_ccd.getNumber("CCD_EXPOSURE")

        # Ensure the CCD simulator snoops the telescope simulator
        # otherwise you may not have a picture of vega
        ccd_active_devices = self.device_ccd.getText("ACTIVE_DEVICES")
        while not ccd_active_devices:
            time.sleep(0.5)
            ccd_active_devices = self.device_ccd.getText("ACTIVE_DEVICES")

        ccd_active_devices[0].text = "Camera"
        self.indi_client.sendNewText(ccd_active_devices)

        # inform the indi server that we want to receive the "CCD1" blob
        self.indi_client.setBLOBMode(PyIndi.B_ALSO, device_name, "CCD1")

        self.ccd_ccd1 = self.device_ccd.getBLOB("CCD1")
        while not self.ccd_ccd1:
            time.sleep(0.5)
            self.ccd_ccd1 = self.device_ccd.getBLOB("CCD1")

    def capture_single(self, exposure):
        self.ccd_exposure[0].value = exposure
        self.indi_client.sendNewNumber(self.ccd_exposure)

        # could use the event that comes out of this somehow
        self.blob_event_queue.get()

        for blob in self.ccd_ccd1:
            print(f'name: {blob.name} size: {blob.size} format: {blob.format}')
            fits = blob.getblobdata()
            print(f'fits data type: {type(fits)}')

    def capture_sequence(self, exposure, count):

        self.ccd_exposure[0].value = exposure
        self.indi_client.sendNewNumber(self.ccd_exposure)

        for i in range(count):
            # wait for the ith exposure
            self.blob_event_queue.get()
            # we can start immediately the next one
            if i + 1 < count:
                self.ccd_exposure[0].value = exposure
                self.indi_client.sendNewNumber(self.ccd_exposure)
            # and meanwhile process the received one
            for blob in self.ccd_ccd1:
                print(f'name: {blob.name} size: {blob.size} format: {blob.format}')
                # pyindi-client adds a getblobdata() method to IBLOB item
                # for accessing the contents of the blob (bytearray in Python)
                fits = blob.getblobdata()
                print(f'fits data type: {type(fits)}')
                # use astropy.io.fits to make use of the data


cam = IndiCamera()
# cam.capture_single(1)
# 2 FPS max, apparently, and random stalling
cam.capture_sequence(0.01, 10)
