from dataclasses import dataclass

from hti.server.state.events import app_state_event
from hti.server.axes.axis_control import AxisSpeeds
from lib.coordinates import Coordinates


@dataclass
class PECState:
    # Periodic Error Correction
    recording: bool = False
    ready: bool = False
    replaying: bool = False
    factor: float = 1.0


@dataclass
class AppState:
    # Connected cameras by device name
    cameras: dict = None

    annotations: list = None
    axes_connected: bool = False
    axes_sim: bool = False
    steering: bool = False
    guiding: bool = False
    calibrating: bool = False
    target: Coordinates = None
    axis_speeds: AxisSpeeds = None
    last_known_position: dict = None

    pec_state: PECState = PECState()

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        app_state_event(self.__dict__)

    def send_event(self):
        app_state_event(self.__dict__)


@dataclass
class CameraState:
    exposure: float = 1.0
    gain: float = 1.0
    capturing: bool = False
    running_sequence: bool = False
    persist: bool = False
    frame_type: str = 'lights'
