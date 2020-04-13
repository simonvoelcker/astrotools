this.PreviewPage = function(indi) {
    this.indi = indi

    this.setImage = function(url) {
        $('#ccd-preview-image').attr('src', url)
    }

    this.capture = function() {
        let device = indi.devices[current_indi_device()]
        let exposure = $('#exposure').val()
        let gain = $('#gain').val()
        device.capture(exposure, gain)
    }

    this.start_sequence = function() {
        let device = indi.devices[current_indi_device()]
        let exposure = $('#exposure').val()
        let gain = $('#gain').val()
        device.start_sequence(exposure, gain)
        $('#start-sequence').hide()
        $('#stop-sequence').show()
    }

    this.stop_sequence = function() {
        let device = indi.devices[current_indi_device()]
        device.stop_sequence()
        $('#start-sequence').show()
        $('#stop-sequence').hide()
    }

    $('#capture').click(this.capture.bind(this))
    $('#start-sequence').click(this.start_sequence.bind(this))
    $('#stop-sequence').click(this.stop_sequence.bind(this))
    $('#stop-sequence').hide()
}
