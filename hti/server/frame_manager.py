import os
import datetime
import numpy as np
from io import BytesIO
from astropy.io import fits
from PIL import Image


class Frame:
    def __init__(self, fits_data: bytearray, frame_type: str):
        self.fits_data = fits_data
        self.frame_type = frame_type
        self.timestamp = datetime.datetime.now()
        self.persisted = False
        self.pil_image = None

    @property
    def path(self) -> str:
        today = datetime.date.today().isoformat()
        image_name = f'{self.timestamp.isoformat()}.png'
        return os.path.join(today, self.frame_type, image_name)

    def get_pil_image(self):
        if self.pil_image is None:
            fits_file = BytesIO(self.fits_data)
            with fits.open(fits_file) as fits_file:
                numpy_image = np.transpose(fits_file[0].data, (1, 2, 0))
                self.pil_image = Image.fromarray(numpy_image, mode='RGB')
        return self.pil_image

    def get_image_data(self, format: str, downscale: int) -> BytesIO:
        image: Image = self.get_pil_image()
        if downscale > 1:
            width = image.width // downscale
            height = image.height // downscale
            image = image.resize(size=(width, height), resample=Image.NEAREST)

        image_data = BytesIO()
        image.save(image_data, format=format)
        image_data.seek(0)
        return image_data

    def persist(self, path_prefix):
        filepath = os.path.join(path_prefix, self.path)
        directory, filename = os.path.split(filepath)
        os.makedirs(directory, exist_ok=True)
        self.get_pil_image().save(filepath)
        self.persisted = True
        return filepath


class FrameManager:
    MAX_NUM_FRAMES = 10
    """
    Keep track of recently captured frames.
    """
    def __init__(self, static_dir):
        self.static_dir = static_dir
        self.frames = []

    def add_frame(self, frame, persist=False):
        self.frames.append(frame)
        if persist:
            frame.persist(path_prefix=self.static_dir)
        if len(self.frames) > self.MAX_NUM_FRAMES:
            del self.frames[0]

    def get_frame_by_path(self, path):
        try:
            return next(f for f in self.frames if f.path == path)
        except StopIteration:
            return None
