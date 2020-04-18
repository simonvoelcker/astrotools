var indi = new INDI()
indi.get_devices()
var previewPage = new PreviewPage(indi)

var event_handlers = {
    image: (event) => {
        previewPage.setImage(event['image_url'])
    }
}

var events_listener = new EventSource('/events')
events_listener.onmessage = (e) => {
    event = JSON.parse(e.data)
    event_handlers[event['type']](event)
}

var current_indi_device = () => {
    var current_devices = indi.device_names()
    if (current_devices.length == 0)
        return null
    return current_devices[0]
}

$('form').submit((e) => {e.preventDefault()})
