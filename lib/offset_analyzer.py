import os
import json
import numpy as np
import matplotlib.pyplot as plot

from skimage.feature import register_translation
from lib.analyzer import BaseAnalyzer
from lib.util import load_image_greyscale, sigma_clip_dark_end
from lib.frame import Frame


class OffsetAnalyzer(BaseAnalyzer):
    def __init__(self, sigma_threshold, offsets_filepath, offsets_plot_filepath):
        self.sigma_threshold = sigma_threshold
        self.offsets_filepath = offsets_filepath
        self.offsets_plot_filepath = offsets_plot_filepath

        self.reference_frame_image = None
        self.frame_offsets = {}  # use frame as keys

    def analyze_frame(self, frame):
        curr_image = load_image_greyscale(frame.filepath, dtype=np.int16)
        if self.sigma_threshold is not None:
            curr_image = sigma_clip_dark_end(curr_image, self.sigma_threshold)

        if self.reference_frame_image is None:
            self.reference_frame_image = curr_image
            self.frame_offsets[frame] = (0, 0)
        else:
            (offset_x, offset_y), error, _ = register_translation(self.reference_frame_image, curr_image)
            self.frame_offsets[frame] = (offset_x, offset_y)

    def get_results_dict(self, frame: Frame) -> dict:
        return {
            'offset_x': float(self.frame_offsets[frame][0]),
            'offset_y': float(self.frame_offsets[frame][1]),
        }

    def write_results(self):
        self._write_offsets_file()
        self._create_offsets_plot()

    def _write_offsets_file(self):
        filepath = self.offsets_filepath
        offsets_by_file = {
            os.path.basename(frame.filepath): offsets
            for frame, offsets in self.frame_offsets.items()
        }
        with open(filepath, 'w') as f:
            json.dump(offsets_by_file, f, indent=4, sort_keys=True)

    def _create_offsets_plot(self):
        filepath = self.offsets_plot_filepath
        x_offsets = np.array([x for x, y in self.frame_offsets.values()])
        y_offsets = np.array([y for x, y in self.frame_offsets.values()])

        colors = (0, 0, 0)
        area = np.pi * 3

        plot.scatter(x_offsets, y_offsets, s=area, c=colors, alpha=0.5)
        plot.title('Frame offsets')
        plot.xlabel('x')
        plot.ylabel('y')
        plot.savefig(filepath)
