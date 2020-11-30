from datetime import datetime
from influxdb import InfluxDBClient
from simple_pid import PID


class Tracker:
    def __init__(self, config, axis_control, sample_time):
        self.config = config
        self.axis_control = axis_control
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
            self.ra_pid = PID(
                self.config['ra']['pid_p'],
                self.config['ra']['pid_i'],
                self.config['ra']['pid_d'],
                setpoint=0,
            )
            self.ra_pid.output_limits = (-self.config['ra']['range'], self.config['ra']['range'])
            self.ra_pid.sample_time = sample_time

        if 'dec' in self.config:
            self.dec_pid = PID(
                self.config['dec']['pid_p'],
                self.config['dec']['pid_i'],
                self.config['dec']['pid_d'],
                setpoint=0,
            )
            self.dec_pid.output_limits = (-self.config['dec']['range'], self.config['dec']['range'])
            self.dec_pid.sample_time = sample_time

    def on_new_frame(self, frame, path_prefix, status_change_callback=None):
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
