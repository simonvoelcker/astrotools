import PyIndi
import queue


class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
        # to move things out of receiver thread asap
        self.event_queue = queue.Queue()

    def subscribe_for_events(self, event_types: list):
        # TODO should it rather be a receiver queue?
        while True:
            event_type, data = self.event_queue.get()
            if event_type in event_types:
                yield event_type, data

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


if __name__ == '__main__':
    indiclient = IndiClient()
    indiclient.setServer('localhost', 7624)
    indiclient.connectServer()

    event_types = [
        'newSwitch',
        'newNumber',
        'newText',
        'newLight',
        'serverConnected',
        'serverDisconnected',
    ]
    for event_type, data in indiclient.subscribe_for_events(event_types):
        print(f'Event: {event_type}, data: {data}')
