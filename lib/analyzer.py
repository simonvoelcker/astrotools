import datetime
import os

from influxdb import InfluxDBClient

from lib.frame import Frame


class BaseAnalyzer:
    def analyze_frame(self, frame: Frame):
        pass

    def get_results_dict(self, frame: Frame) -> dict:
        # output data to be written to influx
        return {}

    def write_results(self):
        # persist output data in analyzer-specific format
        pass


class Analyzer:
    def __init__(self, analyzers):
        self.analyzers = analyzers
        self.frames = []

    def analyze(self, files):
        self.frames = [Frame(filepath) for filepath in files]

        for frame_index, frame in enumerate(self.frames):
            before = datetime.datetime.now()
            for analyzer in self.analyzers:
                analyzer.analyze_frame(frame)
            after = datetime.datetime.now()
            print(f'[{frame_index + 1}/{len(files)}]: {frame.filepath}. Took {(after - before).seconds}s')

    def write_results(self):
        for analyzer in self.analyzers:
            analyzer.write_results()

    def write_to_influx(self):
        influx_client = InfluxDBClient(
            host='localhost',
            port=8086,
            username='root',
            password='root',
            database='tracking',
        )

        for frame_index, frame in enumerate(self.frames):
            frame_time_posix = frame.get_capture_timestamp()
            frame_time = frame_time_posix.strftime('%Y-%m-%dT%H:%M:%S%Z')

            fields = {
                'filepath': frame.filepath,
                'basename': os.path.basename(frame.filepath),
            }
            for analyzer in self.analyzers:
                fields.update(analyzer.get_results_dict(frame))

            body = [
                {
                    'measurement': 'frame_stats',
                    'tags': {
                        'source': 'analyzer.py',
                    },
                    'time': frame_time,
                    'fields': fields,
                }
            ]
            influx_client.write_points(body)
