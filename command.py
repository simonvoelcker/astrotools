import cmd
import sys
import glob
import os

from steer import AxisControl
from util import locate_image


class CommandShell(cmd.Cmd):
	intro = 'Interactive command shell for telescope control'
	prompt = '>>> '

	axis_control = AxisControl()
	ra_resting_speed = -0.0047
	dec_resting_speed = 0.0

	here = None
	target = None

	image_source_pattern = os.path.join('..', 'beute', '**', '*.tif')

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
		self.here = AxisControl.parse_coordinates(arg)

	def do_target(self, arg):
		self.target = AxisControl.parse_coordinates(arg)

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

	def do_autohere(self, arg):
		all_images = glob.glob(self.image_source_pattern)
		if not all_images:
			print('No images')
			return
		latest_image = max(all_images, key=os.path.getctime)
		self.here = locate_image(latest_image)
		print(f'Found current coordinates to be {self.here} (using image {latest_image})')

	def do_track(self, arg):
		# keep pointing in current direction, image-offset based
		pass

if __name__ == '__main__':
	CommandShell().cmdloop()
