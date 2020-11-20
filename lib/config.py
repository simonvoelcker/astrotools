# absolute paths that should really not exist
SOLVE_BINARY = '/usr/local/astrometry/bin/solve-field'
TARGETS_CATALOG_FILEPATH = '/home/simon/Hobby/astro/astrotools/catalogs/ngc.csv'
STARS_DB_FILEPATH = '/home/simon/Hobby/astro/Tycho-2/tycho2.db'

# pixel scale limits for solve-field. unit is arc seconds per pixel
SOLVE_PIXEL_SCALE_LOW = 0.8
SOLVE_PIXEL_SCALE_HIGH = 1.0

# axis ratios (reduction factor from motor shaft to axis)
RA_AXIS_RATIO = 138.0 * 3.0  # 138: worm gear. 3: belt
DEC_AXIS_RATIO = 88.0 * 2.4  # 88: worm gear. 2.4: spur gears

# maximum axis (not motor shaft) speed in degrees per second
MAX_AXIS_SPEED_DPS = 0.3
