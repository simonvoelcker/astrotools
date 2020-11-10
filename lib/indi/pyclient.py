import PyIndi
import queue
import time

from threading import Thread


class IndiClient(PyIndi.BaseClient):
    def __init__(self, host='localhost', port=7624):
        super(IndiClient, self).__init__()

        # to move things out of receiver thread asap
        self.event_queue = queue.Queue()

        self.setServer(host, port)
        self.connectServer()

    def newDevice(self, device):
        self.event_queue.put(('newDevice', device))

    def newProperty(self, prop):
        self.event_queue.put(('newProperty', prop))

    def removeProperty(self, prop):
        self.event_queue.put(('removeProperty', prop))

    def newBLOB(self, blob):
        self.event_queue.put(('newBlob', blob))

    def newSwitch(self, switch_vector_property):
        self.event_queue.put(('newSwitch', switch_vector_property))

    def newNumber(self, number_vector_property):
        self.event_queue.put(('newNumber', number_vector_property))

    def newText(self, text_vector_property):
        self.event_queue.put(('newText', text_vector_property))

    def newLight(self, light_vector_property):
        self.event_queue.put(('newLight', light_vector_property))

    def newMessage(self, device, message):
        self.event_queue.put(('newMessage', (device, message)))

    def serverConnected(self):
        self.event_queue.put(('serverConnected', None))

    def serverDisconnected(self, code):
        self.event_queue.put(('serverDisconnected', code))

    def subscribe_for_events(self, event_types: list = None):
        while True:
            event_type, data = self.event_queue.get()
            if event_types is None or event_type in event_types:
                yield event_type, data

    # TODO this interface is innapropriate because we lack types.
    # the old interface worked because it was all text based.

    def set_property(self, device, property, element, value):
        self.sendNewSwitch()

    def set_property_sync(self, device, property, element, value, timeout=2):
        pass

    def get_property(self, device, property, element):
        return None


def is_state(s):
    if s == PyIndi.ISS_OFF:
        return "Off"
    else:
        return "On"


def ips_state(s):
    if s == PyIndi.IPS_IDLE:
        return "Idle"
    elif s == PyIndi.IPS_OK:
        return "Ok"
    elif s == PyIndi.IPS_BUSY:
        return "Busy"
    elif s == PyIndi.IPS_ALERT:
        return "Alert"


def pretty_print_property(prop):
    # pretty is relative

    print(f'\n{prop.getGroupName()}, {prop.getName()}')

    if prop.getType() == PyIndi.INDI_TEXT:
        tpy = prop.getText()
        for t in tpy:
            print(f'\t{t.name} ({t.label}) = {t.text}')
    elif prop.getType() == PyIndi.INDI_NUMBER:
        tpy = prop.getNumber()
        for t in tpy:
            print(f'\t{t.name} ({t.label}) = {t.value}')
    elif prop.getType() == PyIndi.INDI_SWITCH:
        tpy = prop.getSwitch()
        for t in tpy:
            print(f'\t{t.name} ({t.label}) = {is_state(t.s)}')
    elif prop.getType() == PyIndi.INDI_LIGHT:
        tpy = prop.getLight()
        for t in tpy:
            print(f'\t{t.name} ({t.label}) = {ips_state(t.s)}')
    elif prop.getType() == PyIndi.INDI_BLOB:
        tpy = prop.getBLOB()
        for t in tpy:
            print(f'\t{t.name} ({t.label}) = <blob {str(t.size)} bytes>')


def receive_and_print(client):
    for event_type, data in client.subscribe_for_events():
        if event_type != 'newProperty':
            print(f'Event: {event_type}, data: {data}')
        if event_type == 'newProperty':
            getters = [
                'getBLOB',
                'getBaseDevice',
                'getDeviceName',
                'getGroupName',
                'getLabel',
                'getLight',
                'getName',
                'getNumber',
                'getPermission',
                'getProperty',
                'getRegistered',
                'getState',
                'getSwitch',
                'getText',
                'getTimestamp',
                'getType',
                'isDynamic',
            ]
            setters = [
                'setBaseDevice',
                'setDynamic',
                'setProperty',
                'setRegistered',
                'setType',
            ]
            # pretty_print_property(data)


if __name__ == '__main__':
    indiclient = IndiClient()

    receiver_thread = Thread(target=receive_and_print, args=(indiclient,))
    receiver_thread.start()

    device_name = 'Toupcam GPCMOS02000KPA'
    device = indiclient.getDevice(device_name)
    while not device:
        print('Waiting for device')
        time.sleep(0.1)
        device = indiclient.getDevice(device_name)

    # wait CONNECTION property be defined for telescope
    connect_switch = device.getSwitch("CONNECTION")
    while not connect_switch:
        print('Waiting for switch')
        time.sleep(0.1)
        connect_switch = device.getSwitch("CONNECTION")

    # if the telescope device is not connected, we do connect it
    if not device.isConnected():
        print('Connecting')
        connect_switch[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
        connect_switch[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
        indiclient.sendNewSwitch(connect_switch)

    print('\n')
    # pp = device.getProperties()
    # for prop in pp:
    #     print(prop.getName())
    #     pretty_print_property(prop)

    p = device.getProperty(f'TC_WB_TT', PyIndi.INDI_NUMBER)
    # it can be None. timing shit going on.
    pretty_print_property(p)

    ps = device.getPropertyState('TC_WB_TT')
    print(ps)

    # indiclient.set_property(device_name, 'CONNECTION', 'CONNECT', 'On')

    while True:
        pass
