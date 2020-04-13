this.PreviewPage = function(localsettings, indi) {
    this.localsettings = localsettings;
    this.indi = indi;
    PreviewPage.SETTING_EXPOSURE='setting_exposure';

    this.setImage = function(url) {
        $('#ccd-preview-image').attr('src', url);
    };

    this.preview = function() {
        this.set_exposure();
        let device = indi.devices[current_indi_device()]
        let exposure = this.exposure()
        device.capture(exposure, 10);
    };

    this.framing = function() {
        this.set_exposure();
        current_indi_device().framing(this.exposure());
        $('#framing').hide();
        $('#stop-framing').show();

    };

    this.stop_framing = function() {
        current_indi_device().stop_framing();
        $('#framing').show();
        $('#stop-framing').hide();
    }

    this.exposure = function() {
        return this.localsettings.get(PreviewPage.SETTING_EXPOSURE, 1);
    };

    this.set_exposure = function(value) {
        if(value === undefined)
            value = $('#exposure').val();
        this.localsettings.set(PreviewPage.SETTING_EXPOSURE, value);
        $('#exposure').val(this.exposure());
    };

    this.onDisplay = function() {
        if(this.localsettings.getJSON('preview_page_first_run', true) == true ) {
            var firstRunCompleted = function(){
                this.localsettings.setJSON('preview_page_first_run', false);
            };
        };
    };

    $('#ccd-preview-image').click(function() {
        $('#ccd-preview-image').toggleClass('img-responsive');
    });

    this.set_exposure(this.exposure());
    $('#preview').click(this.preview.bind(this));
    $('#framing').click(this.framing.bind(this));
    $('#stop-framing').click(this.stop_framing.bind(this));
    $('#stop-framing').hide();
};
