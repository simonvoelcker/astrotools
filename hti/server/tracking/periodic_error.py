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


class PeriodicErrorRecorder:
    def __init__(self):
        self.samples = []
        self.done = False  # a complete round of samples is present

    def add_sample(self, sample):
        if len(self.samples) > 0:
            rounds = sample.wheel_position - self.samples[0].wheel_position
            print(f'PEC recorder: {rounds} rounds completed')
            if rounds > 1:
                print('PEC recorder: finalizing')
                self.finalize()
                return
        self.samples.append(sample)

    def finalize(self):
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
        self.done = True

    def save_recording(self):
        with open('pec_recording.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(['wheel_position', 'pixel_error'])
            for sample in self.samples:
                writer.writerow([sample.wheel_position, sample.pixel_error])

    def sample_pixel_error(self, wheel_position):
        if wheel_position < 0:
            wheel_position += 1
        if wheel_position > 1:
            wheel_position -= 1

        # copy first sample to the end to allow for safe interpolation
        first_sample_wrapped = ErrorSample(
            wheel_position=self.samples[0].wheel_position + 1.0,
            pixel_error=self.samples[0].pixel_error,
        )
        samples_ring = self.samples + [first_sample_wrapped]

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
        epsilon = 0.01
        s1 = self.sample_pixel_error(wheel_position - epsilon)
        s2 = self.sample_pixel_error(wheel_position + epsilon)
        return (s2 - s1) / (2.0 * epsilon)

    def get_speed_correction(self, wheel_position, factor):
        return self.sample_slope(wheel_position) * factor
