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

        self.ccd_controls = get_retry(lambda: self.device_ccd.getNumber("CCD_CONTROLS"))
        assert self.ccd_controls[0].name == 'Gain'
        self.ccd_exposure = get_retry(lambda: self.device_ccd.getNumber("CCD_EXPOSURE"))
        self.ccd_frame = get_retry(lambda: self.device_ccd.getNumber("CCD_FRAME"))
        assert self.ccd_frame[0].name == 'X'
        assert self.ccd_frame[1].name == 'Y'
        assert self.ccd_frame[2].name == 'WIDTH'
        assert self.ccd_frame[3].name == 'HEIGHT'
        self.ccd_binning = get_retry(lambda: self.device_ccd.getNumber("CCD_BINNING"))
        assert self.ccd_binning[0].name == 'HOR_BIN'
        assert self.ccd_binning[1].name == 'VER_BIN'

        self.ccd_active_devices = get_retry(lambda: self.device_ccd.getText("ACTIVE_DEVICES"))
        self.ccd_active_devices[0].text = "Camera"
        self.indi_client.sendNewText(self.ccd_active_devices)

        # inform the indi server that we want to receive the "CCD1" blob
        self.indi_client.setBLOBMode(PyIndi.B_ALSO, device_name, "CCD1")

        self.ccd_ccd1 = get_retry(lambda: self.device_ccd.getBLOB("CCD1"))

    def set_region(self, region):
        if region is None:
            region = [0, 0, 1920, 1080]
        for dim in range(4):
            self.ccd_frame[dim].value = region[dim]
        self.indi_client.sendNewNumber(self.ccd_frame)

    def set_binning(self, binning):
        if binning is None:
            binning = (1, 1)
        self.ccd_binning[0].value = binning[0]
        self.ccd_binning[1].value = binning[1]
        self.indi_client.sendNewNumber(self.ccd_binning)

    def set_gain(self, gain):
        self.ccd_controls[0].value = gain
        self.indi_client.sendNewNumber(self.ccd_controls)

    def start_exposure(self, exposure, ignore_ready=False):
        if not ignore_ready:
            # wait till device is ready
            while self.ccd_exposure.s != PyIndi.IPS_OK:
                time.sleep(0.01)

        self.ccd_exposure[0].value = exposure
        self.indi_client.sendNewNumber(self.ccd_exposure)

    def await_image(self):
        # could use the event that comes out of this somehow,
        # especially if it references the ccd_ccd1 property.
        self.blob_event_queue.get()

    def capture_single(self, exposure, gain, region=None):
        self.set_region(region)
        self.set_gain(gain)
        self.start_exposure(exposure, ignore_ready=True)
        self.await_image()
        return self.ccd_ccd1[0].getblobdata()[:]

    def capture_sequence(self, exposure, gain, region=None, run_while=None):
        self.set_region(region)
        self.set_gain(gain)
        self.start_exposure(exposure, ignore_ready=True)

        while True:
            self.await_image()
            image_data = self.ccd_ccd1[0].getblobdata()[:]
            if run_while and not run_while():
                break
            self.start_exposure(exposure)
            yield image_data
