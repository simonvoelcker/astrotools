from dataclasses import dataclass

from lib.coordinates import Coordinates


@dataclass
class AppState:
    running_sequence: bool = False
    steering: bool = False
    tracking: bool = False
    calibrating: bool = False
    here: Coordinates = None
    target: Coordinates = None