import numpy as np
import queue

from typing import Callable
from datetime import datetime
from influxdb import InfluxDBClient
from simple_pid import PID
from skimage.feature import register_translation

from lib.util import sigma_clip_dark_end

from hti.server.state.events import (
    subscribe_for_events,
    log_event,
    unsubscribe_from_events,
)
from hti.server.capture.frame_manager import FrameManager
from hti.server.axes.axis_control import AxisControl


class AutoGuider:
    """
    Simple image-based guider using PID control.
    """

    def __init__(
        self,
        config: dict,
        device: str,
        axis_control: AxisControl,
        ra_resting_speed_dps: float,
        dec_resting_speed_dps: float,
    ):
        self.config = config
        self.device = device
        self.axis_control = axis_control
        self.reference_image = None
        self.sigma_threshold = config['sigma_threshold']

        # the speeds at the time the guiding started - they include drift
        self.ra_resting_speed_dps = ra_resting_speed_dps
        self.dec_resting_speed_dps = dec_resting_speed_dps

        self.influx_client = InfluxDBClient(
            host='localhost',
            port=8086,
            username='root',
            password='root',
            database='tracking',
        )

        self.ra_pid = None
        self.dec_pid = None

        if 'ra' in self.config:
            self.ra_pid = self._create_pid(self.config['ra'])

        if 'dec' in self.config:
            self.dec_pid = self._create_pid(self.config['dec'])

    @staticmethod
    def _create_pid(pid_config: dict) -> PID:
        return PID(
            Kp=pid_config['pid_p'],
            Ki=pid_config['pid_i'],
            Kd=pid_config['pid_d'],
            setpoint=0,
            output_limits=(-pid_config['range'], pid_config['range']),
        )

    def on_new_frame(self, frame):
        # only process frames from one device
        if frame.device != self.device:
            return

        pil_image = frame.get_pil_image()
        # TODO this assumes a color image
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

        if self.config['ra'].get('enable', True):
            ra_speed = self.ra_resting_speed_dps + self.ra_pid(ra_error)
        else:
            ra_speed = self.ra_resting_speed_dps

        if self.config['dec'].get('enable', True):
            dec_speed = self.dec_resting_speed_dps + self.dec_pid(dec_error)
        else:
            dec_speed = self.dec_resting_speed_dps

        self.axis_control.set_axis_speeds(ra_dps=ra_speed, dec_dps=dec_speed, mode='guiding')
        log_event(f'Guiding. Frame: {frame.path}. Offsets: {(ra_error, dec_error)}')

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

    def write_frame_stats(self, **kwargs):
        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%Z')
        body = [
            {
                'measurement': 'axis_log',
                'tags': {
                    'source': 'track.py',
                },
                'time': now,
                'fields': kwargs,
            }
        ]
        self.influx_client.write_points(body)

    def run_loop(self, frame_manager: FrameManager, run_while: Callable):
        # process most recent events first and discard old ones
        q = queue.LifoQueue()
        subscribe_for_events(q)
        latest_processed_event = None

        while run_while():
            try:
                event = q.get(timeout=1)
            except queue.Empty:
                # re-evaluate run_while
                continue
            if event['type'] != 'image':
                continue
            if latest_processed_event and latest_processed_event['unix_timestamp'] >= event['unix_timestamp']:
                # skip over old events
                continue
            latest_processed_event = event
            frame_path = event['image_path']
            frame = frame_manager.get_frame_by_path(frame_path)
            self.on_new_frame(frame)

        log_event(f'Tracking status: Stopped')
        unsubscribe_from_events(q)
