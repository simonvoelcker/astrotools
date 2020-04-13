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

    this.run_calibration = function() {
        let colors = ['ff0000', '00ff00', '0000ff', 'ffff00', '00ffff', 'ff00ff'] //, '000000', 'ffffff']
        for (var i=0; i<colors.length; i++) {
            $('#calibration_area').css("background-color", colors[i])
        }
    }

    $('#capture').click(this.capture.bind(this))
    $('#start-sequence').click(this.start_sequence.bind(this))
    $('#stop-sequence').click(this.stop_sequence.bind(this))
    $('#stop-sequence').hide()
    $('#calibrate').click(this.run_calibration.bind(this))
}
