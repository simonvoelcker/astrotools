import json
import os

from lib.analyzer import BaseAnalyzer
from lib.solver import Solver
from lib.frame import Frame


class CalibrationAnalyzer(BaseAnalyzer):
    def __init__(self, calibration_data_filepath=None):
        self.calibration_data = {}
        self.calibration_data_filepath = calibration_data_filepath

    def analyze_frame(self, frame: Frame):
        self.calibration_data[frame] = Solver().analyze_image(frame.filepath, timeout=15)

    def get_results_dict(self, frame) -> dict:
        data = self.calibration_data.get(frame)
        if data is None:
            return {}

        return {
            'center_ra_deg': data.center_deg.ra,
            'center_dec_deg': data.center_deg.dec,
            'parity': bool(data.parity == 'pos'),
            'pixel_scale': data.pixel_scale,
            'pixel_scale_unit': data.pixel_scale_unit,
            'rotation_angle': data.rotation_angle,
            'rotation_direction': data.rotation_direction,
        }

    def write_results(self):
        filepath = self.calibration_data_filepath
        calibration_data_by_file = {
            os.path.basename(frame.filepath): calibration_data.to_dict()
            for frame, calibration_data in self.calibration_data.items()
            if calibration_data
        }
        with open(filepath, 'w') as f:
            json.dump(calibration_data_by_file, f, indent=4, sort_keys=True)

