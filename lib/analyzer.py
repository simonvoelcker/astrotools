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


class AnalyzerGroup(BaseAnalyzer):
    def __init__(self):
        self.analyzers = []
        self.frames = []

    def add_analyzer(self, analyzer):
        self.analyzers.append(analyzer)

    def analyze_frame(self, frame: Frame):
        for analyzer in self.analyzers:
            analyzer.analyze_frame(frame)
        self.frames.append(frame)

    def write_results(self):
        for analyzer in self.analyzers:
            analyzer.write_results()

    def get_results_dict(self, frame: Frame) -> dict:
        results = {}
        for analyzer in self.analyzers:
            results.update(analyzer.get_results_dict(frame))
        return results

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
            fields.update(self.get_results_dict(frame))

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
