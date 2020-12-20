import csv

from dataclasses import dataclass
from itertools import tee


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


@dataclass
class ErrorSample:
    wheel_position: float = None
    pixel_error: float = None


class PeriodicErrorManager:
    def __init__(self, pec_state):
        self.samples = []
        self.pec_state = pec_state

    def add_sample(self, sample):
        if len(self.samples) > 0:
            rounds = sample.wheel_position - self.samples[0].wheel_position
            print(f'PEC recorder: {rounds} rounds completed')
            if rounds > 1:
                print('PEC recorder: finalizing')
                self._finalize_recording()
                return
        self.samples.append(sample)

    def _finalize_recording(self):
        drift = self.samples[-1].pixel_error - self.samples[0].pixel_error

        # subtract increasing portions of the drift from samples' pixel errors
        for sample in self.samples:
            rounds = sample.wheel_position - self.samples[0].wheel_position
            sample.pixel_error -= drift * rounds

        # normalize wheel positions by subtracting integer part
        for sample in self.samples:
            sample.wheel_position -= int(sample.wheel_position)

        # offset samples to have sampling period start at 0 wheel position
        while self.samples[0].wheel_position > self.samples[-1].wheel_position:
            self.samples = self.samples[1:] + self.samples[:1]

        self.save_recording()
        self.pec_state.recording = False
        self.pec_state.ready = True

    def save_recording(self):
        with open('pec_recording.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(['wheel_position', 'pixel_error'])
            for sample in self.samples:
                writer.writerow([sample.wheel_position, sample.pixel_error])

    def sample_pixel_error(self, wheel_position):
        if wheel_position < 0:
            wheel_position += abs(wheel_position) + 1
        if wheel_position > 1:
            wheel_position -= int(wheel_position)

        # copy first+last sample to the end to allow for safe interpolation
        first_sample_wrapped = ErrorSample(
            wheel_position=self.samples[0].wheel_position + 1.0,
            pixel_error=self.samples[0].pixel_error,
        )
        last_sample_wrapped = ErrorSample(
            wheel_position=self.samples[-1].wheel_position - 1.0,
            pixel_error=self.samples[-1].pixel_error,
        )
        samples_ring = [last_sample_wrapped] + self.samples + [first_sample_wrapped]

        def fraction(low, middle, high):
            return (middle - low) / (high - low)

        def lerp(low_value, high_value, f):
            return low_value * (1.0-f) + high_value * f

        for s1, s2 in pairwise(samples_ring):
            if s1.wheel_position <= wheel_position < s2.wheel_position:
                f = fraction(s1.wheel_position, wheel_position, s2.wheel_position)
                return lerp(s1.pixel_error, s2.pixel_error, f)

        print('WARN: Sampling pixel error from PEC recording failed')
        return 0.0

    def sample_slope(self, wheel_position):
        # sampling radius for slope (=speed) computation
        # this should roughly equal a 5-second window
        epsilon = 2.5 / 640.0
        s1 = self.sample_pixel_error(wheel_position - epsilon)
        s2 = self.sample_pixel_error(wheel_position + epsilon)
        # unit is pixels/second, roughly equal to arcsecs/second
        return (s2 - s1) / 5.0

    def get_speed_correction(self, wheel_position, range):
        correction = self.sample_slope(wheel_position) * self.pec_state.factor
        print(self.sample_slope(wheel_position), self.pec_state.factor, correction)
        correction = min(range, max(-range, correction))
        return correction
