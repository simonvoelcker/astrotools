import queue

from typing import Callable
from datetime import datetime
from influxdb import InfluxDBClient
from simple_pid import PID

from hti.server.state.events import (
    subscribe_for_events,
    log_event,
    unsubscribe_from_events,
)
from hti.server.capture.frame_manager import Frame, FrameManager
from hti.server.axes.axis_control import AxisControl
from hti.server.tracking.periodic_error import PeriodicErrorManager


class Tracker:
    def __init__(
        self,
        config: dict,
        device: str,
        axis_control: AxisControl,
        pec_manager: PeriodicErrorManager,
        sample_time: float,
        ra_resting_speed_dps: float,
        dec_resting_speed_dps: float,
    ):
        self.config = config
        self.device = device
        self.axis_control = axis_control
        self.pec_manager = pec_manager
        # the speeds at the time the tracking started - they include drift
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
            self.ra_pid = self._create_pid(self.config['ra'], sample_time)

        if 'dec' in self.config:
            self.dec_pid = self._create_pid(self.config['dec'], sample_time)

    @staticmethod
    def _create_pid(pid_config: dict, sample_time: float) -> PID:
        return PID(
            Kp=pid_config['pid_p'],
            Ki=pid_config['pid_i'],
            Kd=pid_config['pid_d'],
            setpoint=0,
            sample_time=sample_time,
            output_limits=(-pid_config['range'], pid_config['range']),
        )

    def on_new_frame(self, frame: Frame):
        raise NotImplementedError

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

    def run_tracking_loop(self, frame_manager: FrameManager, run_while: Callable):
        # process most recent events first and discard old ones
        q = queue.LifoQueue()
        subscribe_for_events(q)
        latest_processed_event = None

        while run_while():
            event = q.get()
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
