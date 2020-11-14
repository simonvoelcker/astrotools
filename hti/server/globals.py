import os

from hti.server.app_state import AppState
from lib.catalog import Catalog
from lib.axis_control import AxisControl
from lib.indi.controller import INDIController, INDIControllerMock

_app_state = AppState()
_app_state.axes_sim = os.environ.get('SIM_AXES', 'false').lower() == 'true'
_app_state.camera_sim = os.environ.get('SIM_CAMERA', 'false').lower() == 'true'
_catalog = Catalog()
_indi_controller = None
_axis_control = None


def get_app_state():
    global _app_state
    return _app_state


def get_catalog():
    global _catalog
    return _catalog


def get_indi_controller():
    global _indi_controller
    if _indi_controller is None:
        here = os.path.dirname(os.path.abspath(__file__))
        hti_static_dir = os.path.join(here, '..', 'static')
        sim_mode = os.environ.get('SIM_CAMERA', 'false').lower() == 'true'
        if sim_mode:
            _indi_controller = INDIControllerMock(static_dir=hti_static_dir)
        else:
            _indi_controller = INDIController(static_dir=hti_static_dir)
            get_app_state().camera_connected = bool(_indi_controller.devices())
    return _indi_controller


def get_axis_control():
    global _axis_control
    if _axis_control is None:
        def on_speeds_change(speeds):
            get_app_state().axis_speeds = speeds
        _axis_control = AxisControl(on_speeds_change)
        sim_mode = os.environ.get('SIM_AXES', 'false').lower() == 'true'
        if not sim_mode:
            _axis_control.connect()
            get_app_state().axes_connected = _axis_control.connected()
    return _axis_control
