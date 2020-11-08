import subprocess
import re
import os
import glob

from PIL import Image

solve_binary = '/usr/local/astrometry/bin/solve-field'
xy2rd_binary = '/usr/local/astrometry/bin/wcs-xy2rd'

ra_dec_rx = re.compile(r'.*RA,Dec \((?P<ra>[\d.\-]+), (?P<dec>[\d.\-]+)\).*')


def xy_to_rd_dict(wcs_file: str, x: int, y: int) -> dict:
    command = [xy2rd_binary, '-w', wcs_file, '-x', str(x), '-y', str(y)]
    output = subprocess.check_output(command).decode()
    return ra_dec_rx.match(output).groupdict()


def get_image_config(image_path: str) -> dict:
    # solve field
    wcs_file = 'wcs.wcs'
    command = [
        solve_binary,
        image_path,
        '--no-plots',
        '--temp-axy',
        '--solved', 'none',
        '--corr', 'none',
        '--new-fits', 'none',
        '--index-xyls', 'none',
        '--match', 'none',
        '--rdls', 'none',
        '--wcs', wcs_file,
    ]
    subprocess.check_output(command)

    # describe corners xy, convert to rd
    width, height = Image.open(image_path).size
    corners_xy = [
        (0, 0),
        (0, height-1),
        (width-1, 0),
        (width-1, height-1),
    ]
    corners_rd = [
        xy_to_rd_dict(wcs_file, xy[0], xy[1])
        for xy in corners_xy
    ]

    return {
        'path': os.path.basename(image_path),
        'size': {'width': width, 'height': height},
        'corners': corners_rd
    }


def handle_directory(directory: str):
    image_paths = glob.glob(os.path.join(directory, '*.png'))
    config = [
        get_image_config(path)
        for path in image_paths
    ]
    print(config)


path = '/home/simon/Hobby/astro/Hall Of Fame/'
handle_directory(path)
