import os
import json

from .periodic_error import PeriodicErrorManager
from .tracker import Tracker
from .target_tracker import TargetTracker
from .image_tracker import ImageTracker
from .passive_tracker import PassiveTracker

from hti.server.axes.axis_control import AxisControl


def create_tracker(
    mode: str,
    device: str,
    frame_cadence: float,
    axis_control: AxisControl,
    pec_manager: PeriodicErrorManager,
) -> Tracker:
    config_file = {
        'target': 'track_target_config.json',
        'image': 'track_image_config.json',
        'passive': 'track_passively_config.json',
    }[mode]

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, config_file), 'r') as f:
        config = json.load(f)

    tracker_class = {
        'target': TargetTracker,
        'image': ImageTracker,
        'passive': PassiveTracker,
    }[mode]

    return tracker_class(
        config,
        device,
        axis_control,
        pec_manager,
        frame_cadence,
        axis_control.speeds.ra_dps,  # use current speeds as defaults
        axis_control.speeds.dec_dps,
    )
