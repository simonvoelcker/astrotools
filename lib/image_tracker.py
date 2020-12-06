import numpy as np

from skimage.feature import register_translation

from lib.util import sigma_clip_dark_end
from lib.tracker import Tracker

from PIL import ImageFilter


class ImageTracker(Tracker):

    def __init__(
        self,
        config,
        axis_control,
        sample_time,
        ra_resting_speed_dps,  # not necessarily the siderial speed
        dec_resting_speed_dps,
    ):
        super().__init__(config, axis_control, sample_time)
        self.reference_image = None
        self.sigma_threshold = config['sigma_threshold']
        self.ra_resting_speed_dps = ra_resting_speed_dps
        self.dec_resting_speed_dps = dec_resting_speed_dps

    def on_new_frame(self, frame, path_prefix, status_change_callback=None):

        pil_image = frame.get_pil_image()
        image = np.transpose(np.asarray(pil_image), (1, 0, 2))
        image_for_offset_detection = sigma_clip_dark_end(image, self.sigma_threshold)

        if self.reference_image is None:
            self.reference_image = image_for_offset_detection
            status_change_callback(message='Using reference frame', filepath=frame.path)
            return

        (ra_error, dec_error), _, __ = register_translation(self.reference_image, image_for_offset_detection)

        if self.config['ra']['invert']:
            ra_error = -ra_error
        if self.config['dec']['invert']:
            dec_error = -dec_error

        ra_speed = self.ra_resting_speed_dps + self.ra_pid(ra_error)
        dec_speed = self.dec_resting_speed_dps + self.dec_pid(dec_error)

        self.axis_control.set_axis_speeds(ra_dps=ra_speed, dec_dps=dec_speed, mode='tracking')
        status_change_callback(message='Tracking', filepath=frame.path, errors=(ra_error, dec_error))

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
            )

    @staticmethod
    def pick_guiding_region(frame, radius):
        image = frame.get_pil_image()
        image = image.crop((
            radius,
            radius,
            image.width - radius,
            image.height - radius,
        ))
        image = image.filter(filter=ImageFilter.GaussianBlur(5))
        np_image = np.asarray(image)
        np_image = np.mean(np_image, axis=2)
        np_image = np.flip(np_image, axis=0)

        max_point = np.unravel_index(np.argmax(np_image), np_image.shape)

        # square region of given radius around the brightest pixel
        # because of cropping earlier, this is offset by 1*region_radius
        return {
            'x': max_point[1].item(),
            'y': max_point[0].item(),
            'width': 2 * radius,
            'height': 2 * radius,
        }
