import csv

from dataclasses import dataclass


class Vect:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Vect(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vect(self.x * scalar, self.y * scalar)


@dataclass
class ErrorSample:
    ra_wheel_position: float = None
    ra_pixel_error: float = None
    x_pixel_error: float = None
    y_pixel_error: float = None

    def __init__(self, ra_wheel_position, x_pixel_error, y_pixel_error):
        self.ra_wheel_position = ra_wheel_position
        self.x_pixel_error = x_pixel_error
        self.y_pixel_error = y_pixel_error

    def as_vect(self):
        return Vect(self.x_pixel_error, self.y_pixel_error)


@dataclass
class CleanedErrorSample:
    ra_wheel_position: float = None
    ra_pixel_error: float = None


class PeriodicErrorRecorder:
    def __init__(self):
        self.samples = []
        self.done = False  # a complete round of samples is present

    def add_sample(self, sample):
        if len(self.samples) > 0:
            rounds = sample.ra_wheel_position - self.samples[0].ra_wheel_position
            print(f'PEC recorder: {rounds} rounds completed')
            if rounds > 1:
                print('PEC recorder: finalizing')
                self.finalize()
                return
        self.samples.append(sample)

    def finalize(self):
        self.save_samples()

        # compute drift vector: last sample minus first one
        drift_vect = self.samples[-1].as_vect() - self.samples[0].as_vect()

        # subtract increasing portions of drift_vect from samples' error vects
        for sample in self.samples:
            wheel_position = sample.ra_wheel_position - self.samples[0].ra_wheel_position
            drift_vect_so_far = drift_vect * wheel_position
            pixel_error_vect = sample.as_vect() - drift_vect_so_far
            sample.ra_pixel_error = pixel_error_vect.x

        # normalize wheel positions by subtracting integer part
        for sample in self.samples:
            sample.ra_wheel_position -= int(sample.ra_wheel_position)

        # offset samples to have sampling period start at 0 wheel position
        while self.samples[0].ra_wheel_position > self.samples[-1].ra_wheel_position:
            self.samples = self.samples[1:] + self.samples[:1]

        self.save_recording()
        self.done = True

    def save_samples(self):
        with open('pec_samples.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(['wheel_position', 'x_pixel_error', 'y_pixel_error'])
            for sample in self.samples:
                writer.writerow([
                    sample.ra_wheel_position,
                    sample.x_pixel_error,
                    sample.y_pixel_error,
                ])

    def save_recording(self):
        with open('pec_recording.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(['wheel_position', 'pixel_error'])
            for sample in self.samples:
                writer.writerow([
                    sample.ra_wheel_position,
                    sample.ra_pixel_error,
                ])
