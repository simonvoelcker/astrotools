import os
import math
import datetime


class Frame:

    def __init__(self, filepath, metadata=None):
        self.filepath = filepath
        self.metadata = metadata

        self._pixel_offset = None
        self._angle = None

    def get_capture_timestamp(self):
        # take this info from the filename, if properly formatted.
        basename = os.path.basename(self.filepath)

        try:
            # filename example: 2021-02-22T20:28:40.162488.png
            timestamp = datetime.datetime.strptime(basename, '%Y-%m-%dT%H:%M:%S.%f.png')
        except ValueError:
            # fall back to timestamp of file creation.
            timestamp = os.path.getctime(self.filepath)
        return timestamp

    @property
    def center(self):
        center_deg = self.metadata['center_deg']
        return float(center_deg['ra']), float(center_deg['dec'])

    @property
    def angle(self):
        return self._angle or float(self.metadata['rotation_angle'])

    @property
    def parity(self):
        return self.metadata['parity']['parity'] == 'pos'

    @property
    def pixel_scale(self):
        # unit is assumed to be arcseconds per pixel,
        # but can be found in self.metadata['pixel_scale_unit']
        return float(self.metadata['pixel_scale'])

    @property
    def pixel_offset(self):
        return self._pixel_offset

    def set_pixel_offset(self, pixel_offset):
        self._pixel_offset = pixel_offset

    def set_angle(self, angle):
        self._angle = angle

    def to_pixels(self, point_deg, pixel_scale_aspp):
        ra_aspp = pixel_scale_aspp / math.cos(math.radians(self.center[1]))
        dec_aspp = pixel_scale_aspp
        x_px = -point_deg[0] * 3600.0 / ra_aspp
        y_px = point_deg[1] * 3600.0 / dec_aspp
        return x_px, y_px

    def get_offset_degrees(self, reference_frame):
        if reference_frame == self:
            return 0, 0

        offset_x_deg = self.center[0] - reference_frame.center[0]
        offset_y_deg = self.center[1] - reference_frame.center[1]
        return offset_x_deg, offset_y_deg

    def get_pixel_offset(self, reference_frame, pixel_scale_aspp):
        offset_deg = (self.center[0] - reference_frame.center[0],
                      self.center[1] - reference_frame.center[1])
        return self.to_pixels(offset_deg, pixel_scale_aspp)

    @classmethod
    def compute_frame_offsets(cls, frames, custom_offset=None):
        # average pixel scale
        pixel_scales = [frame.pixel_scale for frame in frames]
        average_pixel_scale_aspp = sum(pixel_scales) / len(pixel_scales)

        if custom_offset is not None:
            custom_x, custom_y = custom_offset.split(',')
            custom_x, custom_y = float(custom_x), float(custom_y)
        else:
            custom_x, custom_y = 0, 0

        # compute pixel offsets to reference frame
        reference_frame = frames[0]
        for frame_index, frame in enumerate(frames):
            offset = frame.get_pixel_offset(reference_frame, average_pixel_scale_aspp)

            # apply additional custom offset if given
            offset = (offset[0] + custom_x * float(frame_index) / float(len(frames) - 1),
                      offset[1] + custom_y * float(frame_index) / float(len(frames) - 1))

            frame.set_pixel_offset(offset)

        # subtract min offset to it is zero and we only need to care about max
        min_offset_x = min(frame.pixel_offset[0] for frame in frames)
        min_offset_y = min(frame.pixel_offset[1] for frame in frames)
        for frame in frames:
            frame.set_pixel_offset((int(frame.pixel_offset[0] - min_offset_x),
                                    int(frame.pixel_offset[1] - min_offset_y)))

    @staticmethod
    def interpolate_angles(frames):
        # pretty cheap but it works for now
        first, last = frames[0].angle, frames[-1].angle
        for frame_index, frame in enumerate(frames):
            frame.set_angle(first + (last - first) * frame_index / (len(frames) - 1))
