import glob
import itertools
import numpy as np
import os
import subprocess
import time

from PIL import Image
from skimage.filters import laplace, sobel

# TODO utils should not import from lib
from lib.image_stack import ImageStack


def run_command_or_die_trying(command, timeout, run_callback=None):
    # Popen accepts a timeout parameter, but it does not work smh
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL)
    while timeout > 0:
        if process.poll() is not None:
            output = process.stdout.read().decode()
            return output
        if run_callback is not None and not run_callback():
            # abort
            break
        time.sleep(1)
        timeout -= 1
    process.kill()
    return None


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
    print(
        f'Found {len(files)} frames in {directory} - Creating an average frame')
    average_frame = ImageStack.create_average_frame(directory, files,
                                                    color_mode)
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
    yxc_image = np.zeros((yx_image.shape[0], yx_image.shape[1], 3),
                         dtype=np.int8)
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
    pil_images[0].save(filename, save_all=True, append_images=pil_images[1:],
                       duration=50, loop=0)


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


def pairwise(iterable):
    # s -> (s0,s1), (s1,s2), (s2, s3), ...
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
