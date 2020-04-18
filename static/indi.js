var INDIDevice = function(devicename, properties) {
    this.name = devicename
    this.properties = properties

    this.reload = function(callback, devicename) {
        $.ajax(this.__url(['properties']), {success: this.__got_properties.bind(this, callback)})
    }

    this.get = function(property, callback) {
        $.ajax(this.__url(['properties', property]), {success: this.__got_property.bind(this, callback)})
    }

    this.set = function(property, value, callback) {
        let request_options = {
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({value: value}),
            success: this.__got_property.bind(this, callback)
        }
        $.ajax(this.__url(['properties', property]), request_options)
    }

    this.filter_properties = function(property, element) {
        return properties.filter(function(each) {
            var matches = true
            if (property !== undefined)
                matches &= each['property'] == property
            if (element !== undefined)
                matches &= each['element'] == element
            return matches
        })
    }

    this.capture = function(exposure, gain) {
        $.ajax(this.__url(['capture', exposure, gain]))
    } 

    this.start_sequence = function(pathprefix, exposure, gain) {
        let request_options = {
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                pathprefix: pathprefix,
                exposure: exposure,
                gain: gain
            })
        }
        $.ajax(this.__url(['start_sequence']), request_options)
    }

    this.stop_sequence = function() {
        $.ajax(this.__url(['stop_sequence']))
    }

    this.__got_properties = function(callback, data) {
        this.properties = data['properties']
        if (callback !== undefined)
            callback(this)
    }

    this.__got_property = function(callback, data) {
        if (callback !== undefined)
            callback(data, this)
    }

    this.__url = function(suburl) {
        if (suburl === undefined)
            suburl = []
        return ['/device', this.name].concat(suburl).join('/')
    }
}

var INDI = function() {

    this.devices = {}

    this.get_devices = function(callback) {
        $.ajax('/devices', {success: this.__got_devices.bind(this, callback)})
    }

    this.device_names = function() {
        return Object.keys(this.devices)
    }

    this.__got_devices = function(callback, data) {
        this.devices = {}
        Object.keys(data).forEach(function(name) {
            this.devices[name] = new INDIDevice(name, data[name])
        }, this)
        if (callback)
            callback(this)
    }
}
