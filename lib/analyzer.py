import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import os

from influxdb import InfluxDBClient
from skimage.feature import register_translation

from lib.frame import Frame
from lib.util import load_image_greyscale, sigma_clip_dark_end


class Analyzer:

    def __init__(self, sigma_threshold):
        self.sigma_threshold = sigma_threshold
        self.reference_frame_image = None

        # map frames to frame metadata
        self.frame_offsets = {}
        self.astrometric_metadata = {}
        self.frame_brightness = {}

    def get_astrometric_metadata_hint(self):
        for metadata in self.astrometric_metadata.values():
            if metadata is not None:
                return {
                    'ra': metadata['center_deg']['ra'],
                    'dec': metadata['center_deg']['dec'],
                    'radius': 1.0,
                }
        return None

    def analyze(self, files):
        for frame_index, filepath in enumerate(files):
            before = datetime.datetime.now()
            self.analyze_frame(Frame(filepath))
            after = datetime.datetime.now()
            print(f'Processed frame {frame_index + 1}/{len(files)}: {filepath}. Took {(after - before).seconds}s')

    def analyze_frame(self, frame):
        hint = self.get_astrometric_metadata_hint()
        self.astrometric_metadata[frame] = frame.compute_astrometric_metadata(hint)
        image_greyscale = load_image_greyscale(frame.filepath, dtype=np.int16)
        self.frame_brightness[frame] = np.average(image_greyscale)
        self.frame_offsets[frame] = self.get_offsets(image_greyscale)

    def get_offsets(self, image_greyscale):
        curr_image = image_greyscale
        if self.sigma_threshold is not None:
            curr_image = sigma_clip_dark_end(curr_image, self.sigma_threshold)

        if self.reference_frame_image is None:
            self.reference_frame_image = curr_image
            return 0, 0

        (offset_x, offset_y), error, _ = register_translation(self.reference_frame_image, curr_image)
        return offset_x, offset_y

    def write_astrometric_metadata(self, directory, filename='astrometric_metadata.json'):
        filepath = os.path.join(directory, filename)
        metadata_by_file = {
            os.path.basename(frame.filepath): metadata
            for frame, metadata in self.astrometric_metadata.items()
        }
        with open(filepath, 'w') as f:
            json.dump(metadata_by_file, f, indent=4, sort_keys=True)

    def write_offsets_file(self, directory, filename='offsets.json'):
        filepath = os.path.join(directory, filename)
        offsets_by_file = {
            os.path.basename(frame.filepath): offsets
            for frame, offsets in self.frame_offsets.items()
        }
        with open(filepath, 'w') as f:
            json.dump(offsets_by_file, f, indent=4, sort_keys=True)

    def create_offsets_plot(self, filename):
        x_offsets = np.array([x for x, y in self.frame_offsets.values()])
        y_offsets = np.array([y for x, y in self.frame_offsets.values()])

        colors = (0, 0, 0)
        area = np.pi * 3

        plt.scatter(x_offsets, y_offsets, s=area, c=colors, alpha=0.5)
        plt.title('Frame offsets')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.savefig(filename)

    def write_to_influx(self):
        influx_client = InfluxDBClient(host='localhost', port=8086, username='root', password='root',
                                       database='tracking')

        frames = list(self.frame_offsets.keys())

        frame_0_time_posix = os.path.getctime(frames[0].filepath)
        exposure = 15

        for frame_index, frame in enumerate(frames):
            frame_time_posix = frame_0_time_posix + frame_index * exposure
            frame_time = datetime.datetime.utcfromtimestamp(frame_time_posix).strftime('%Y-%m-%dT%H:%M:%S%Z')
            print(f'Frame {os.path.basename(frame.filepath)}: Time={frame_time}')

            fields = {
                'filepath': frame.filepath,
                'basename': os.path.basename(frame.filepath),
                'time_posix': float(frame_time_posix),
            }
            metadata = self.astrometric_metadata[frame]
            if metadata is not None:
                fields.update({
                    'center_ra': metadata['center']['ra'],
                    'center_dec': metadata['center']['dec'],
                    'center_ra_deg': float(metadata['center_deg']['ra']),
                    'center_dec_deg': float(metadata['center_deg']['dec']),
                    'parity': bool(metadata['parity']['parity'] == 'pos'),
                    'pixel_scale': float(metadata['pixel_scale']['scale']),
                    'pixel_scale_unit': metadata['pixel_scale']['unit'],
                    'rotation_angle': float(metadata['rotation']['angle']),
                    'rotation_direction': metadata['rotation']['direction'],
                    'size_width': float(metadata['size']['width']),
                    'size_height': float(metadata['size']['height']),
                    'size_unit': metadata['size']['unit'],
                    'offset_x': float(self.frame_offsets[frame][0]),
                    'offset_y': float(self.frame_offsets[frame][1]),
                    'brightness': float(self.frame_brightness[frame]),
                })

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
