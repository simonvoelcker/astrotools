class INDIDevice {
    constructor(devicename, properties) {
        this.name = devicename
        this.properties = properties
    }

    reload(callback, devicename) {
        $.ajax(this._url(['properties']), {success: this._got_properties.bind(this, callback)})
    }

    get(property, callback) {
        $.ajax(this._url(['properties', property]), {success: this._got_property.bind(this, callback)})
    }

    set(property, value, callback) {
        let request_options = {
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({value: value}),
            success: this._got_property.bind(this, callback)
        }
        $.ajax(this._url(['properties', property]), request_options)
    }

    filter_properties(property, element) {
        return properties.filter((each) => {
            var matches = true
            if (property !== undefined)
                matches &= each['property'] == property
            if (element !== undefined)
                matches &= each['element'] == element
            return matches
        })
    }

    capture(exposure, gain) {
        $.ajax(this._url(['capture', exposure, gain]))
    } 

    start_sequence(pathprefix, exposure, gain) {
        let request_options = {
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                pathprefix: pathprefix,
                exposure: exposure,
                gain: gain
            })
        }
        $.ajax(this._url(['start_sequence']), request_options)
    }

    stop_sequence() {
        $.ajax(this._url(['stop_sequence']))
    }

    _got_properties(callback, data) {
        this.properties = data['properties']
        if (callback !== undefined)
            callback(this)
    }

    _got_property(callback, data) {
        if (callback !== undefined)
            callback(data, this)
    }

    _url(suburl) {
        if (suburl === undefined)
            suburl = []
        return ['/device', this.name].concat(suburl).join('/')
    }
}

class INDI {
    constructor() {
        this.devices = {}
    }

    get_devices(callback) {
        $.ajax('/devices', {success: this._got_devices.bind(this, callback)})
    }

    device_names() {
        return Object.keys(this.devices)
    }

    _got_devices(callback, data) {
        this.devices = {}
        Object.keys(data).forEach((name) => {
            this.devices[name] = new INDIDevice(name, data[name])
        }, this)
        if (callback)
            callback(this)
    }
}
