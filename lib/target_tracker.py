import time

from lib.axis_control import AxisSpeeds
from lib.solver import Solver
from lib.tracker import Tracker


class TargetTracker(Tracker):
    def __init__(self, config, axis_control):
        super().__init__(config, axis_control)
        self.target = None

    def set_target(self, target):
        self.target = target

    def _get_tracking_mode_config(self, ra_error, dec_error):
        # get the appropriate tracking mode config for the current error
        for mode_config in self.config['modes']:
            max_error = mode_config['max_error_deg']
            if max_error is None or (abs(ra_error) < max_error and abs(dec_error) < max_error):
                print(f'RA err: {ra_error:.2f}, Dec err: {dec_error:.2f} => Mode: {mode_config["name"]}')
                return mode_config
        raise RuntimeError(f'Found no tracking mode config for given error: RA={ra_error}, Dec={dec_error}')

    def on_new_file(self, filepath, status_change_callback=None):
        image_coordinates = Solver().locate_image(filepath)

        if not image_coordinates:
            self.axis_control.set_motor_speed('A', AxisSpeeds.ra_resting_speed)
            self.axis_control.set_motor_speed('B', AxisSpeeds.dec_resting_speed)
            status_change_callback(message='Calibration failed, using default speeds', filepath=filepath)
            return

        ra_error = image_coordinates.ra - self.target.ra
        dec_error = image_coordinates.dec - self.target.dec

        mode_config = self._get_tracking_mode_config(ra_error, dec_error)

        if 'Steering' in mode_config['name']:
            status_change_callback(message='Steering to target', filepath=filepath, errors=(ra_error, dec_error))
            self.axis_control.steer(
                here=image_coordinates,
                target=self.target,
                max_speed_dps=mode_config['max_speed_dps'],
            )
            status_change_callback(message='Waiting for axes to settle', filepath=filepath)
            time.sleep(mode_config['delay_after_maneuver_sec'])
            return

        ra_speed = self.config['ra']['center'] + self.ra_pid(-ra_error if self.config['ra']['invert'] else ra_error)
        dec_speed = self.config['dec']['center'] + self.dec_pid(-dec_error if self.config['dec']['invert'] else dec_error)

        print(f'RA error: {ra_error:8.6f}, DEC error: {dec_error:8.6f}, '
              f'RA speed: {ra_speed:8.6f}, DEC speed: {dec_speed:8.6f}')

        self.axis_control.set_motor_speed('A', ra_speed)
        self.axis_control.set_motor_speed('B', dec_speed)

        status_change_callback(message='Tracking', filepath=filepath, errors=(ra_error, dec_error))

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
