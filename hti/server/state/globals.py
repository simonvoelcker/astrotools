import os

from hti.server.state.app_state import AppState, CameraState

from hti.server.capture.frame_manager import FrameManager
from hti.server.capture.camera_controller import CameraController, SimCameraController
from hti.server.guiding.periodic_error import PeriodicErrorManager
from hti.server.catalog import Catalog
from hti.server.axes.axis_control import AxisControl
from hti.server.stacking.image_stacker import ImageStacker

_app_state = AppState()
_app_state.axes_sim = os.environ.get('SIM_AXES', 'false').lower() == 'true'
_app_state.camera_sim = os.environ.get('SIM_CAMERA', 'false').lower() == 'true'
_catalog = Catalog()
_cam_controller = None
_axis_control = None
_frame_manager = None
_pec_manager = None
_image_stacker = None


def get_app_state():
    global _app_state
    return _app_state


def get_catalog():
    global _catalog
    return _catalog


def get_camera_controller():
    global _cam_controller
    if _cam_controller is None:
        sim_mode = os.environ.get('SIM_CAMERA', 'false').lower() == 'true'
        if sim_mode:
            _cam_controller = SimCameraController()
        else:
            _cam_controller = CameraController()

        get_app_state().cameras = {
            device_name: CameraState(
                **_cam_controller.get_device_capabilities(device_name),
            )
            for device_name in _cam_controller.get_device_names()
        }

    return _cam_controller


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


def get_frame_manager():
    global _frame_manager
    if _frame_manager is None:
        here = os.path.dirname(os.path.abspath(__file__))
        hti_static_dir = os.path.join(here, '..', 'static')
        _frame_manager = FrameManager(hti_static_dir)
    return _frame_manager


def get_pec_manager():
    global _pec_manager
    if _pec_manager is None:
        _pec_manager = PeriodicErrorManager(get_app_state().pec_state)
    return _pec_manager


def get_image_stacker():
    global _image_stacker
    if _image_stacker is None:
        _image_stacker = ImageStacker()
    return _image_stacker
