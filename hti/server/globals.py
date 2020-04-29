import os
from lib.catalog import Catalog
from lib.indi.controller import INDIController

_app_state = None
_indi_controller = None
_catalog = None


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
        workdir = os.path.join(here, '..', '..', 'static', 'images')
        _indi_controller = INDIController(workdir)
    return _indi_controller
