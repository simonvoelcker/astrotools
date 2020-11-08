from dataclasses import dataclass

from hti.server.api.events import app_state_event
from lib.axis_control import AxisSpeeds
from lib.coordinates import Coordinates


@dataclass
class AppState:
    capturing: bool = False
    running_sequence: bool = False
    steering: bool = False
    tracking: bool = False
    calibrating: bool = False
    target: Coordinates = None
    axis_speeds: AxisSpeeds = None
    last_known_position: dict = None
    last_calibration_result: dict = None

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        app_state_event(self.__dict__)
