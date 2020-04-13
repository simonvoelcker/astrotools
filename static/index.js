var json_request = function(url, data, options) {
    var request_options = {method: 'PUT', data: JSON.stringify(data), contentType: 'application/json' }
    if(options !== undefined) {
        $.extend(request_options, options);
    }
    $.ajax(url, request_options);
};



var indi = new INDI();
indi.get_devices();

var localSettings = new LocalSettings()
var previewPage = new PreviewPage(localSettings, indi);


var event_handlers = {
    image: function(event) {
        previewPage.setImage(event['image_url']);
        $('.image-received-notification').remove();
    },
};

var events_listener = new EventSource('/events');
events_listener.onmessage = function(e) {
    event = JSON.parse(e.data);
    event_handlers[event['type']](event);
};

var current_indi_device = function() {
    var current_devices = indi.device_names();
    if(current_devices.length == 0)
        return null;
    return current_devices[0]
};

var on_server_status = function(status) {
    var text = 'server is idle.';
    if(status['shooting']) {
        var elapsed = Number(status['now'] - status['started']).toFixed(1);
        var remaining = Number(status['exposure'] - elapsed).toFixed(1);
        text = 'server is currently shooting: exposure is ' + Number(status['exposure']).toFixed(1) + 's, elapsed: ' + elapsed + 's, remaining: ' + remaining + 's.';
    }
    $('.server-status-notification').remove();
    notification('info', 'Server Status', text, {timeout: 5, additional_class: 'server-status-notification'});
};

$('#server-status').click(function() { $.ajax('/status', {success: on_server_status}); });

$('form').submit(function(e){e.preventDefault()});
