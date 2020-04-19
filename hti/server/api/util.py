import os

subscriptions = []


def subscribe_for_events(sub):
    subscriptions.append(sub)

def put_event(event):
    for subscription in subscriptions:
        subscription.put(event)

def image_event(image_filepath):
    put_event({
        'type': 'image',
        'image_url': os.path.join('static', 'images', image_filepath) ,
        'image_id': '6174'
    })

def notification(level, title, message):
    put_event({
        'type': 'notification',
        'level': level,
        'title': title,
        'message': message
    })
