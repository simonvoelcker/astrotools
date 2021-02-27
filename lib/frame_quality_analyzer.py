import numpy as np

from lib.analyzer import BaseAnalyzer
from lib.frame import Frame
from lib.util import load_image_greyscale


class FrameQualityAnalyzer(BaseAnalyzer):
    def __init__(self):
        self.frame_brightness = {}  # key is frame

    def analyze_frame(self, frame: Frame):
        image_greyscale = load_image_greyscale(frame.filepath, dtype=np.int16)
        self.frame_brightness[frame] = np.average(image_greyscale)

    def get_results_dict(self, frame: Frame) -> dict:
        return {
            'brightness': float(self.frame_brightness[frame]),
        }

    def write_results(self):
        # fancy plots go here
        pass
