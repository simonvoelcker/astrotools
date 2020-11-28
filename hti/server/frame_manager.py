import numpy as np
from io import BytesIO
from dataclasses import dataclass

from astropy.io import fits
from PIL import Image


@dataclass
class Frame:
    path: str = None
    timestamp: int = None
    fits_data: bytearray = None
    persisted: bool = False

    def get_image_data(self, format: str) -> BytesIO:
        fits_file = BytesIO(self.fits_data)
        image_data = BytesIO()
        with fits.open(fits_file) as fits_file:
            numpy_image = np.transpose(fits_file[0].data, (1, 2, 0))
            pil_image = Image.fromarray(numpy_image, mode='RGB')
            pil_image.save(image_data, format=format)
        image_data.seek(0)
        return image_data


class FrameManager:
    MAX_NUM_FRAMES = 5
    """
    Keep track of recently captured frames.
    """
    def __init__(self, static_dir):
        self.static_dir = static_dir
        self.frames = []

    def add_frame(self, frame):
        self.frames.append(frame)
        if len(self.frames) > self.MAX_NUM_FRAMES:
            del self.frames[0]

    def get_frame_by_path(self, path):
        try:
            return next(f for f in self.frames if f.path == path)
        except StopIteration:
            return None

    def persist_frame(self, path):
        pass
        # out_dir = os.path.join(self.static_dir, path_prefix)
        # os.makedirs(out_dir, exist_ok=True)
        # filepath = os.path.join(out_dir, image_name)
