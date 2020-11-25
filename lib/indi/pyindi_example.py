import PyIndi
import time
import sys
import threading


class IndiClient(PyIndi.BaseClient):
    def __init__(self, host, port, blob_event):
        super(IndiClient, self).__init__()

        self.blob_event = blob_event

        # connect
        self.setServer(host, port)
        if not (self.connectServer()):
            print(f'Server not running: {host}:{port}')
            sys.exit(1)

    def newDevice(self, d):
        pass

    def newProperty(self, p):
        pass

    def removeProperty(self, p):
        pass

    def newBLOB(self, bp):
        self.blob_event.set()

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

        # what a spooky way of getting the data
        self.blob_event = threading.Event()

        # connect the server
        self.indi_client = IndiClient('localhost', 7624, self.blob_event)

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

        # we should inform the indi server that we want to receive the
        # "CCD1" blob from this device
        self.indi_client.setBLOBMode(PyIndi.B_ALSO, device_name, "CCD1")

    def capture(self):

        ccd_ccd1 = self.device_ccd.getBLOB("CCD1")
        while not ccd_ccd1:
            time.sleep(0.5)
            ccd_ccd1 = self.device_ccd.getBLOB("CCD1")

        # a list of our exposure times
        exposures = [1.0, 5.0]

        # we use here the threading.Event facility of Python
        # we define an event for newBlob event
        self.blob_event.clear()
        i = 0
        self.ccd_exposure[0].value = exposures[i]
        self.indi_client.sendNewNumber(self.ccd_exposure)

        while i < len(exposures):
            # wait for the ith exposure
            self.blob_event.wait()
            # we can start immediately the next one
            if i + 1 < len(exposures):
                self.ccd_exposure[0].value = exposures[i + 1]
                self.blob_event.clear()
                self.indi_client.sendNewNumber(self.ccd_exposure)
            # and meanwhile process the received one
            for blob in ccd_ccd1:
                print(f'name: {blob.name} size: {blob.size} format: {blob.format}')
                # pyindi-client adds a getblobdata() method to IBLOB item
                # for accessing the contents of the blob (bytearray in Python)
                fits = blob.getblobdata()
                print(f'fits data type: {type(fits)}')
                # use astropy.io.fits to make use of the data
            i += 1


cam = IndiCamera()
cam.capture()
