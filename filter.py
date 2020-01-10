import math

from util import pairwise


class Filter:
	def __init__(self, angular_distance_threshold):
		self.angular_distance_threshold = angular_distance_threshold

	def apply(self, frames):
		discarded_frames = set()
		distances = []
		for frame_1, frame_2 in pairwise(frames):
			if frame_1.metadata is None or frame_2.metadata is None:
				discarded_frames.update({frame_1, frame_2})
				continue
			ra_ofs, dec_ofs = frame_1.get_offset_degrees(frame_2)
			angular_distance = math.hypot(ra_ofs, dec_ofs)
			if angular_distance > self.angular_distance_threshold:
				discarded_frames.update({frame_1, frame_2})
			distances.append(angular_distance)

		frames_to_keep = [frame for frame in frames if frame not in discarded_frames]
		print(f'Keeping {len(frames_to_keep)} of {len(frames)} frames')
		if distances:
			print(f'Frame-over-frame distances '\
				  f'average={sum(distances)/len(distances):.4f} '\
				  f'min={min(distances):.4f} '\
				  f'max={max(distances):.4f}')
		return frames_to_keep
