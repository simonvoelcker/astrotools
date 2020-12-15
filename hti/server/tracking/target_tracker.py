import os

from lib.solver import Solver
from .tracker import Tracker
from ..state.events import log_event


class TargetTracker(Tracker):
    def __init__(
        self,
        config,
        axis_control,
        sample_time,
        ra_resting_speed_dps,  # not necessarily the siderial speed
        dec_resting_speed_dps,
     ):
        super().__init__(config, axis_control, sample_time)
        self.target = None
        self.ra_resting_speed_dps = ra_resting_speed_dps
        self.dec_resting_speed_dps = dec_resting_speed_dps

    def set_target(self, target):
        self.target = target

    def on_new_frame(self, frame):
        here = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.normpath(os.path.join(here, '..', '..', 'static', frame.path))
        image_coordinates = Solver().locate_image(filepath)

        if not image_coordinates:
            self.axis_control.set_axis_speeds(
                ra_dps=self.ra_resting_speed_dps,
                dec_dps=self.dec_resting_speed_dps,
                mode='resting',
            )
            log_event(f'Calibration failed, using default speeds. File: {filepath}')
            return

        ra_error = image_coordinates.ra - self.target.ra
        dec_error = image_coordinates.dec - self.target.dec

        if self.config['ra']['invert']:
            ra_error = -ra_error
        if self.config['dec']['invert']:
            dec_error = -dec_error

        ra_speed = self.ra_resting_speed_dps + self.ra_pid(ra_error)
        dec_speed = self.dec_resting_speed_dps + self.dec_pid(dec_error)

        self.axis_control.set_axis_speeds(
            ra_dps=ra_speed,
            dec_dps=dec_speed,
            mode='tracking',
        )

        log_event(f'Tracking. File: {filepath}. Errors: {(ra_error, dec_error)}')

        if self.influx_client is not None:
            self.write_frame_stats(
                file_path=filepath,
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
