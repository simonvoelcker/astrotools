# absolute paths that should really not exist
SOLVE_BINARY = '/usr/local/astrometry/bin/solve-field'
TARGETS_CATALOG_FILEPATH = '/home/simon/Hobby/astro/astrotools/catalogs/NGC.csv'
STARS_DB_FILEPATH = '/home/simon/Hobby/astro/Tycho-2/tycho2.db'

# pixel scale limits for solve-field. unit is arc seconds per pixel
SOLVE_PIXEL_SCALE_LOW = 0.6
SOLVE_PIXEL_SCALE_HIGH = 1.0

# axis ratios (reduction factor from motor shaft to axis)
RA_AXIS_RATIO = 138.0 * 3.0  # 138: worm gear. 3: belt
DEC_AXIS_RATIO = 88.0 * 2.4  # 88: worm gear. 2.4: spur gears

# maximum axis (not motor shaft) speed in degrees per second
MAX_AXIS_SPEED_DPS = 0.3

# TODO get this info automatically from the INDI server -> just use props in FE instead?

# GET /api/cameras
# GET /api/cameras/1/props
# PUT /api/cameras/1/props ...

# we NEED to store some of this stuff in BE as well, though
# so why not have a translation layer, at least

CAMERAS = [
    {
        "name": "ZWO CCD ASI178MM",
        "frame_width": 3096,
        "frame_height": 2080,
        "color": False,
        "min_gain": 1,  # TODO test
        "max_gain": 400,  # TODO test
        "min_exposure": 32 / 1000000,
        "max_exposure": 1000,
    },
    {
        "name": "Toupcam GPCMOS02000KPA",
        "frame_width": 1920,
        "frame_height": 1080,
        "color": True,
        "min_gain": 20000,  # TODO test
        "max_gain": 20000,  # TODO test
        "min_exposure": 105 / 1000000,
        "max_exposure": 1000,
    },
]

DEFAULT_CAPTURING_CAMERA = "ZWO CCD ASI178MM"
DEFAULT_GUIDING_CAMERA = "Toupcam GPCMOS02000KPA"
