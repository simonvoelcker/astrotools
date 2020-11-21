import glob
import os
import time

from datetime import datetime

from influxdb import InfluxDBClient
from simple_pid import PID


class Tracker:
    def __init__(self, config, axis_control, sample_time):
        self.config = config
        self.image_search_pattern = self.config.get('image_search_pattern')

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

    def track(self):
        known_files = set(glob.glob(self.image_search_pattern))

        while True:
            all_files = set(glob.glob(self.image_search_pattern))
            new_files = all_files - known_files
            time.sleep(0.5)  # wait here, not above, to be sure the new file is complete on disk
            if not new_files:
                continue
            known_files = all_files
            if len(new_files) > 1:
                print(f'WARN: Found {len(new_files)} new images at once')
            newest_file = max(new_files, key=os.path.getctime)
            print(f'Handling new file: {newest_file}')
            self.on_new_file(newest_file)

    def on_new_file(self, filepath, status_change_callback=None):
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
