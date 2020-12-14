import cmd
import glob
import os

from lib.axis_control import AxisControl
from lib.catalog import Catalog
from lib.coordinates import Coordinates
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
		self.axis_control.connect()

	def do_disconnect(self, arg):
		if not self.axis_control.connected():
			print('Not connected')
			return
		self.axis_control.disconnect()

	def do_rest(self, arg):
		print('Setting axes to resting speed')
		self.axis_control.set_resting()

	def do_stop(self, arg):
		print('Stopping axes')
		self.axis_control.set_axis_speeds(ra_dps=0.0, dec_dps=0.0, mode='stopped')

	def do_ra(self, arg):
		print(f'Setting RA axis speed to {float(arg)}')
		self.axis_control.set_axis_speeds(ra_dps=float(arg), mode='manual')

	def do_dec(self, arg):
		print(f'Setting DEC axis speed to {float(arg)}')
		self.axis_control.set_axis_speeds(dec_dps=float(arg), mode='manual')

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


if __name__ == '__main__':
	CommandShell().cmdloop()
