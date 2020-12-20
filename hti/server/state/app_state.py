from dataclasses import dataclass

from .events import app_state_event
from lib.axis_control import AxisSpeeds
from lib.coordinates import Coordinates


@dataclass
class PECState:
    # Periodic Error Correction
    recording: bool = False
    ready: bool = False
    correcting: bool = False
    factor: float = 0.0


@dataclass
class AppState:
    camera_connected: bool = False
    camera_sim: bool = False
    axes_connected: bool = False
    axes_sim: bool = False

    capturing: bool = False
    running_sequence: bool = False
    steering: bool = False
    guiding: bool = False
    calibrating: bool = False
    target: Coordinates = None
    axis_speeds: AxisSpeeds = None
    last_known_position: dict = None

    annotations: list = None

    pec_state: PECState = PECState()

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        app_state_event(self.__dict__)
