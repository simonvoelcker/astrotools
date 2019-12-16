import cmd
import sys
import glob
import os

from steer import AxisControl
from util import locate_image
from coordinates import Coordinates
from catalog import Catalog


class CommandShell(cmd.Cmd):
	intro = 'Interactive command shell for telescope control'
	prompt = '>>> '

	axis_control = AxisControl()
	ra_resting_speed = -0.0047
	dec_resting_speed = 0.0

	here = None
	target = None

	image_source_pattern = os.path.join('..', 'beute', '**', '*.tif')

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

	def do_set_image_source_pattern(self, arg):
		self.image_source_pattern = arg

	def do_list_images(self, args):
		for f in glob.glob(self.image_source_pattern):
			print(f)

	def do_sync(self, arg):
		# update self.here to match what's in the latest image

		all_images = glob.glob(self.image_source_pattern)
		if not all_images:
			print('No images')
			return

		latest_image = max(all_images, key=os.path.getctime)
		self.here = locate_image(latest_image)
		if self.here is None:
			print(f'Failed to determine coordinates from image {latest_image}')
			return

		print(f'Current coordinates: {self.here} ({self.here.format()}) (using image {latest_image})')

		if self.target:
			diff = Coordinates(self.target.ra - self.here.ra, self.target.dec - self.here.dec)
			print(f'Target difference: {diff} ({diff.format()})')

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

if __name__ == '__main__':
	CommandShell().cmdloop()
