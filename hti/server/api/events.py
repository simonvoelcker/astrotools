import time

subscriptions = set()


def subscribe_for_events(sub):
    subscriptions.add(sub)


def unsubscribe_from_events(sub):
    subscriptions.remove(sub)


def put_event(event):
    for subscription in subscriptions:
        subscription.put(event)


def image_event(image_path):
    # path is relative to /static/
    put_event({
        'type': 'image',
        'unix_timestamp': time.time(),
        'image_path': image_path,
    })


def tracking_status_event(message, **kwargs):
    put_event({
        'type': 'tracking_status',
        'unix_timestamp': time.time(),
        'message': message,
        'details': kwargs,
    })