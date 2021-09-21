import csv
import datetime

from dataclasses import dataclass
from itertools import tee


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def fraction(low, middle, high):
    return (middle - low) / (high - low)


def lerp(low_value, high_value, f):
    return low_value * (1.0 - f) + high_value * f


def fract_part(value):
    if value < 0:
        value += abs(value) + 1
    if value > 1:
        value -= int(value)
    return value


@dataclass
class ErrorSample:
    wheel_position: float = None
    pixel_error: float = None


class Recording:
    def __init__(self):
        self.samples = []
        self.finalized = False

    def add_sample(self, sample):
        if len(self.samples) > 0:
            rounds = sample.wheel_position - self.samples[0].wheel_position
            print(f'PEC recorder: {int(100.0*rounds)}% completed')
            if rounds > 1 and not self.finalized:
                print('PEC recorder: finalizing')
                self._finalize()
                return
        self.samples.append(sample)

    def _finalize(self):
        drift = self.samples[-1].pixel_error - self.samples[0].pixel_error
        print(f'Drift: {drift}px ({drift/640.0}px/s)')

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

        # persist the recording for analysis on a cloudy day
        self._save()
        self.finalized = True

    def _save(self):
        now = datetime.datetime.now().isoformat()
        with open(f'pec_recording_{now}.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(['wheel_position', 'pixel_error'])
            for sample in self.samples:
                writer.writerow([sample.wheel_position, sample.pixel_error])

    def sample_pixel_error(self, wheel_position):
        wheel_position = fract_part(wheel_position)

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

        for s1, s2 in pairwise(samples_ring):
            if s1.wheel_position <= wheel_position < s2.wheel_position:
                f = fraction(s1.wheel_position, wheel_position, s2.wheel_position)
                return lerp(s1.pixel_error, s2.pixel_error, f)

        print('WARN: Sampling pixel error from PEC recording failed')
        return 0.0

    def sample_slope(self, wheel_position):
        # sampling radius for slope (=speed) computation
        # this should roughly equal a 10-second window
        epsilon = 5.0 / 640.0
        s1 = self.sample_pixel_error(wheel_position - epsilon)
        s2 = self.sample_pixel_error(wheel_position + epsilon)
        # unit is pixels/second, roughly equal to arcsecs/second
        return (s2 - s1) / 10.0


class PeriodicErrorManager:
    def __init__(self, pec_state):
        self.recordings = []
        self.pec_state = pec_state

    def add_sample(self, sample):
        # create new recording if necessary
        if not self.recordings or self.recordings[-1].finalized:
            self.recordings.append(Recording())
        # append to latest recording
        self.recordings[-1].add_sample(sample)
        # ready when first recording is ready
        if self.recordings[0].finalized:
            self.pec_state.ready = True

    def get_speed_correction(self, wheel_position, range_dps):
        if not self.recordings or not self.recordings[0].finalized:
            print('WARN: Not ready to sample PEC recording')
            return 0.0

        slope = self.recordings[0].sample_slope(wheel_position)
        correction = slope * self.pec_state.factor
        correction = min(range_dps, max(-range_dps, correction))
        print(f'Slope: {slope} Factor: {self.pec_state.factor} => Correction: {correction} (capped to {range_dps})')
        return correction
