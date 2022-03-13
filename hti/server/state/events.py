import time

subscriptions = set()


def subscribe_for_events(sub):
    subscriptions.add(sub)


def unsubscribe_from_events(sub):
    subscriptions.remove(sub)


def put_event(event):
    for subscription in subscriptions:
        subscription.put(event)


def app_state_event(app_state):
    put_event({
        'type': 'app_state',
        'unix_timestamp': time.time(),
        'app_state': app_state,
    })


def image_event(device_name, image_path):
    # path is relative to /static/
    put_event({
        'type': 'image',
        'unix_timestamp': time.time(),
        'device_name': device_name,
        'image_path': image_path,
    })


def log_event(text):
    put_event({
        'type': 'log',
        'unix_timestamp': time.time(),
        'text': text,
    })


def sequences_event(sequences):
    put_event({
        'type': 'sequences',
        'unix_timestamp': time.time(),
        'sequences': sequences,
    })
