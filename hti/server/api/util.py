import os

subscriptions = []


def subscribe_for_events(sub):
    subscriptions.append(sub)


def put_event(event):
    for subscription in subscriptions:
        subscription.put(event)


def image_event(image_url):
    put_event({
        'type': 'image',
        'image_url': image_url
    })


def notification(level, title, message):
    put_event({
        'type': 'notification',
        'level': level,
        'title': title,
        'message': message
    })
