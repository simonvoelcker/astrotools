import glob
import itertools
import numpy as np
import os

from PIL import Image
from influxdb import InfluxDBClient
from skimage.filters import laplace, sobel

from lib.image_stack import ImageStack


def load_image(filename, dtype=np.int16):
    pil_image = Image.open(filename)
    yxc_image = np.asarray(pil_image, dtype=dtype)
    xyc_image = np.transpose(yxc_image, (1, 0, 2))
    return xyc_image


def load_image_greyscale(filename, dtype=np.int16):
    pil_image = Image.open(filename).convert('L')
    yx_image = np.asarray(pil_image, dtype=dtype)
    xy_image = np.transpose(yx_image, (1, 0))
    return xy_image


def create_average_frame(directory, search_pattern, color_mode):
    if directory is None:
        return None
    full_search_pattern = os.path.join(directory, search_pattern)
    files = glob.glob(full_search_pattern)
    print(f'Found {len(files)} frames in {directory} - Creating an average frame')
    average_frame = ImageStack.create_average_frame(directory, files, color_mode)
    return average_frame


def save_image(image, filename):
    if image.shape[2] == 1:
        save_image_greyscale(image[:, :, 0], filename)
        return

    yxc_image = np.transpose(image, (1, 0, 2))
    yxc_image = yxc_image.astype(np.int8)
    pil_image = Image.fromarray(yxc_image, mode='RGB')
    pil_image.save(filename)


def save_image_greyscale(image, filename):
    yx_image = np.transpose(image, (1, 0))
    yx_image = yx_image.astype(np.int8)
    # convert to RGB, ghetto style
    yxc_image = np.zeros((yx_image.shape[0], yx_image.shape[1], 3), dtype=np.int8)
    yxc_image[:, :, 0] = yx_image
    yxc_image[:, :, 1] = yx_image
    yxc_image[:, :, 2] = yx_image
    pil_image = Image.fromarray(yxc_image, mode='RGB')
    pil_image.save(filename)


def save_animation(frames, filename, dtype=np.int8):
    # (1) need to pick R channel and store as greyscale
    pil_images = []
    for index, frame in enumerate(frames):
        yxc_image = np.transpose(frame, (1, 0, 2))
        yxc_image = yxc_image.astype(np.int8)[:, :, 0]
        pil_image = Image.fromarray(yxc_image, mode='L')
        pil_images.append(pil_image)
    pil_images[0].save(filename, save_all=True, append_images=pil_images[1:], duration=50, loop=0)


def get_sharpness_aog(frame):
    # average of gradient
    gy, gx = np.gradient(frame)
    gnorm = np.sqrt(gx ** 2 + gy ** 2)
    return np.average(gnorm)


def get_sharpness_vol(frame):
    # variance of laplacian on a downscaled image
    return laplace(frame).var()


def get_sharpness_sobel(frame):
    # variance of sobel
    return sobel(frame).var()


def sigma_clip_dark_end(image, sigma):
    # clip darkest pixels to given multiple of standard deviations above average
    image_greyscale = np.mean(image, axis=2)
    stddev = np.std(image_greyscale)
    average = np.average(image_greyscale)
    # clip away background noise, as indicated by stddev and average
    return np.clip(image_greyscale, average + sigma * stddev, 255)


def query_offsets(path_prefix):
    # WIP and maybe a bad idea.
    # should keep tracking and alignment cleanly separated, in prep for a guiding camera.

    # Usage: query_offsets('../beute/191013')
    path_prefix = path_prefix.replace('/', '\\/')
    influx_client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='tracking')
    offsets_query = f'SELECT ra_image_error, dec_image_error, file_path ' \
                    f'FROM axis_log WHERE file_path =~ /{path_prefix}*/ ORDER BY time ASC'

    offsets_result = influx_client.query(offsets_query)
    # it will remain influxDBs secret why this is so complicated
    rows = offsets_result.items()[0][1]
    return {row['file_path']: (row['ra_image_error'], row['dec_image_error']) for row in rows}


def pairwise(iterable):
    # s -> (s0,s1), (s1,s2), (s2, s3), ...
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
