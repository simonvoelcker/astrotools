import numpy as np
import math

from lib.analyzer import BaseAnalyzer
from lib.frame import Frame
from lib.util import load_image_greyscale

from scipy.ndimage.filters import gaussian_filter


class FrameQualityAnalyzer(BaseAnalyzer):
    def __init__(self):
        self.frame_quality_metrics = {}  # key is frame

    def analyze_frame(self, frame: Frame):
        image_greyscale = load_image_greyscale(frame.filepath, dtype=np.int16)

        self.frame_quality_metrics[frame] = {
            'brightness': float(np.average(image_greyscale)),
            'hfd': self.compute_hfd(image_greyscale),
        }

    def get_results_dict(self, frame: Frame) -> dict:
        return self.frame_quality_metrics[frame]

    def write_results(self):
        # fancy plots go here
        pass

    def compute_hfd(self, image_greyscale):
        # Compute the Half Flux Diameter
        roi = self.get_roi(image_greyscale)
        # Subtract background noise
        roi = np.clip(np.subtract(roi, np.median(roi)), 0, 255)

        # Collect pixel values along with their distance to the center of ROI
        distance_and_brightness = []
        width, height = roi.shape
        for x, y in np.ndindex(roi.shape):
            # Compute distance to center - Squared distance is sufficient
            distance = (width/2-x)*(width/2-x) + (height/2-y)*(height/2-y)
            # Store distance along with pixel value
            distance_and_brightness.append((distance, roi[x, y]))

        # Sort by distance, increasing
        distance_and_brightness.sort(key=lambda entry: entry[0])

        # Find index at which cumulative flux is half of total
        total_flux = np.sum(roi)
        cumulative_flux = 0
        for index, (_, brightness) in enumerate(distance_and_brightness):
            cumulative_flux += brightness
            if 2*cumulative_flux >= total_flux:
                hfd = math.sqrt(2.0 * index / math.pi)
                # save_image_greyscale(roi, f'out/hfd_{hfd:5.2f}.png')
                return hfd
        raise ValueError('Failed to compute HFD')

    def get_roi(self, image_greyscale, radius=50):
        # Get the region surrounding the brightest star
        # Blurring is applied to filter out hot pixels
        # and also to better find the centroid of the star.

        blurred = gaussian_filter(image_greyscale, sigma=5)
        cropped = blurred[radius:-radius, radius:-radius]
        max_point = np.unravel_index(np.argmax(cropped), cropped.shape)
        y, x = max_point[1].item(), max_point[0].item()

        roi = image_greyscale[x:x+2*radius+1, y:y+2*radius+1]
        return roi
