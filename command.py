import cmd
import glob
import json
import os

from lib.axis_control import AxisControl
from lib.catalog import Catalog
from lib.coordinates import Coordinates
from lib.image_tracker import ImageTracker
from lib.target_tracker import TargetTracker
from lib.passive_tracker import PassiveTracker
from lib.solver import Solver


class CommandShell(cmd.Cmd):
	intro = 'Interactive command shell for telescope control'
	prompt = '>>> '

	axis_control = AxisControl()
	ra_resting_speed = -0.004725
	dec_resting_speed = 0.000075

	here = None
	target = None

	catalog = Catalog()

	def do_exit(self, arg):
		return True

	def do_connect(self, arg):
		if self.axis_control.connected():
			print('Already connected')
			return
		self.axis_control.connect(usb_ports=[0,1])

	def do_disconnect(self, arg):
		if not self.axis_control.connected():
			print('Not connected')
			return
		self.axis_control.disconnect()

	def do_rest(self, arg):
		print('Setting motors to resting speed')
		self.axis_control.set_motor_speed('A', self.ra_resting_speed)
		self.axis_control.set_motor_speed('B', self.dec_resting_speed)

	def do_stop(self, arg):
		print('Stopping motors')
		self.axis_control.set_motor_speed('A', 0)
		self.axis_control.set_motor_speed('B', 0)		

	def do_ra(self, arg):
		print(f'Setting RA motor speed to {float(arg)}')
		self.axis_control.set_motor_speed('A', float(arg))

	def do_dec(self, arg):
		print(f'Setting DEC motor speed to {float(arg)}')
		self.axis_control.set_motor_speed('B', float(arg))

	def do_here(self, arg):
		self.here = Coordinates.parse(arg)

	def do_target(self, arg):
		self.target = Coordinates.parse(arg)

	def do_steer(self, arg):
		if not self.here:
			print('No current coordinate set')
			return
		if not self.target:
			print('No target coordinate set')
			return
		try:
			self.axis_control.steer(self.here, self.target)
		except KeyboardInterrupt:
			print('Maneuver aborted')
			self.do_rest(arg=None)

	def do_sync(self, arg):
		# update self.here to match what's in the latest image

		all_images = glob.glob('../beute/**/*.tif')
		if not all_images:
			print('No images')
			return

		latest_image = max(all_images, key=os.path.getctime)

		image_metadata = None
		try:
			image_metadata = Solver().analyze_image(latest_image)
		except KeyboardInterrupt:
			print('Sync aborted')
			return

		if image_metadata is None:
			print(f'Failed to determine coordinates from image {latest_image}')
			return

		ra, dec = float(image_metadata['center_deg']['ra']), float(image_metadata['center_deg']['dec'])
		angle, direction = float(image_metadata['rotation']['angle']), image_metadata['rotation']['direction']

		self.here = Coordinates(ra, dec)

		print(f'Current coordinates: {self.here}. Rotation angle: {angle:.1f}°{direction}. (from {latest_image})')

		if self.target:
			diff = Coordinates(self.target.ra - self.here.ra, self.target.dec - self.here.dec)
			print(f'Target difference: {diff}')

	def do_lookup(self, arg):
		entry = self.catalog.get_entry(arg)
		print(f'Found entry: {entry}')

	def do_targetobject(self, arg):
		catalog = Catalog()
		entry = catalog.get_entry(arg)
		if entry is None:
			print('No entry found')
			return
		coordinates = Coordinates.parse_csvformat(entry['RA'], entry['Dec'])
		print(f'Setting target coordinates: {coordinates}')
		self.target = coordinates

	def do_trackhere(self, arg):
		if self.here is None:
			print('Where am I?')
			return
		self.target = self.here
		self.do_tracktarget(arg)

	def do_tracktarget(self, arg):
		if self.target is None:
			print('No target set')
			return

		config_file = arg or 'track_target_config.json'
		with open(config_file, 'r') as f:
			config = json.load(f)

		tracker = TargetTracker(config, self.axis_control)
		tracker.set_target(self.target)
		try:
			print(f'Tracking {self.target}')
			tracker.track()
		except KeyboardInterrupt:
			print('Tracking aborted')

	def do_trackimage(self, arg):
		config_file = arg or 'track_image_config.json'
		with open(config_file, 'r') as f:
			config = json.load(f)

		tracker = ImageTracker(config, self.axis_control)
		try:
			print(f'Tracking based on next image')
			tracker.track()
		except KeyboardInterrupt:
			print('Tracking aborted')

	def do_trackpassively(self, arg):
		config_file = arg or 'track_passively_config.json'
		with open(config_file, 'r') as f:
			config = json.load(f)

		tracker = PassiveTracker(config)
		try:
			print(f'Tracking based on next image, passively')
			tracker.track()
		except KeyboardInterrupt:
			print('Tracking aborted')


if __name__ == '__main__':
	CommandShell().cmdloop()
