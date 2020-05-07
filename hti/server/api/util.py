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
        'image_path': image_path,
    })
