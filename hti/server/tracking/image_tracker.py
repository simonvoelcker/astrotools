import numpy as np

from skimage.feature import register_translation

from lib.util import sigma_clip_dark_end
from .tracker import Tracker
from ..state.events import log_event


class ImageTracker(Tracker):

    def __init__(self, config, *args):
        super().__init__(config, *args)
        self.reference_image = None
        self.sigma_threshold = config['sigma_threshold']

    def on_new_frame(self, frame):

        pil_image = frame.get_pil_image()
        image = np.transpose(np.asarray(pil_image), (1, 0, 2))
        image_for_offset_detection = sigma_clip_dark_end(image, self.sigma_threshold)

        if self.reference_image is None:
            self.reference_image = image_for_offset_detection
            log_event(f'Using reference frame: {frame.path}')
            return

        (ra_error, dec_error), _, __ = register_translation(self.reference_image, image_for_offset_detection)

        if self.config['ra']['invert']:
            ra_error = -ra_error
        if self.config['dec']['invert']:
            dec_error = -dec_error

        ra_speed = self.ra_resting_speed_dps + self.ra_pid(ra_error)
        dec_speed = self.dec_resting_speed_dps + self.dec_pid(dec_error)

        self.axis_control.set_axis_speeds(ra_dps=ra_speed, dec_dps=dec_speed, mode='tracking')
        log_event(f'Tracking. File: {frame.path}. Errors: {(ra_error, dec_error)}')

        if self.influx_client is not None:
            self.write_frame_stats(
                file_path=frame.path,
                ra_image_error=float(ra_error),
                ra_speed=float(ra_speed),
                ra_pid_p=float(self.ra_pid.components[0]),
                ra_pid_i=float(self.ra_pid.components[1]),
                ra_pid_d=float(self.ra_pid.components[2]),
                dec_image_error=float(dec_error),
                dec_speed=float(dec_speed),
                dec_pid_p=float(self.dec_pid.components[0]),
                dec_pid_i=float(self.dec_pid.components[1]),
                dec_pid_d=float(self.dec_pid.components[2]),
                brightness=np.average(image),
            )
