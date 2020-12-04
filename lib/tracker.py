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
            self.ra_pid = self._create_pid(self.config['ra'], sample_time)

        if 'dec' in self.config:
            self.dec_pid = self._create_pid(self.config['dec'], sample_time)

    @staticmethod
    def _create_pid(pid_config, sample_time):
        return PID(
            Kp=pid_config['pid_p'],
            Ki=pid_config['pid_i'],
            Kd=pid_config['pid_d'],
            setpoint=0,
            sample_time=sample_time,
            output_limits=(-pid_config['range'], pid_config['range']),
        )

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
