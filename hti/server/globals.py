import os
from lib.catalog import Catalog
from lib.axis_control import AxisControl
from lib.indi.controller import INDIController, INDIControllerMock

_app_state = None
_indi_controller = None
_catalog = None
_axis_control = None


def get_app_state():
    global _app_state
    if _app_state is None:
        _app_state = dict()
    return _app_state


def get_catalog():
    global _catalog
    if _catalog is None:
        _catalog = Catalog()
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
    return _indi_controller


def get_axis_control():
    global _axis_control
    if _axis_control is None:
        _axis_control = AxisControl()
        _axis_control.connect(usb_ports=[0, 1])
    return _axis_control
