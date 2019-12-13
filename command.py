import cmd
import sys
import glob
import os

from steer import AxisControl
from util import locate_image


class CommandShell(cmd.Cmd):
	intro = 'Interactive command shell for telescope control'
	prompt = '>>> '

	axis_control = None
	ra_resting_speed = -0.0047
	dec_resting_speed = 0.0

	here = None
	target = None

	image_source = os.path.join('..', 'beute', '**')

	def do_connect(self, arg):
		if self.axis_control:
			print('Already connected')
			return
		self.axis_control = AxisControl([0, 1])

	def do_disconnect(self, arg):
		if not self.axis_control:
			print('Not connected')
			return
		self.axis_control = None		

	def do_rest(self, arg):
		if not self.axis_control:
			print('Not connected')
			return
		print('Setting motors to resting speed')
		self.axis_control.set_motor_speed('A', self.ra_resting_speed)
		self.axis_control.set_motor_speed('B', self.dec_resting_speed)

	def do_stop(self, arg):
		if not self.axis_control:
			print('Not connected')
			return
		print('Stopping motors')
		self.axis_control.set_motor_speed('A', 0)
		self.axis_control.set_motor_speed('B', 0)		

	def do_ra(self, arg):
		if not self.axis_control:
			print('Not connected')
			return
		print(f'Setting RA motor speed to {float(arg)}')
		self.axis_control.set_motor_speed('A', float(arg))

	def do_dec(self, arg):
		if not self.axis_control:
			print('Not connected')
			return
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
		if not self.axis_control:
			print('Not connected')
			return
		self.axis_control.steer(self.here, self.target)

	def do_set_image_source(self, arg):
		self.image_source = arg

	def do_list_images(self, args):
		search_pattern = os.path.join(self.image_source, '*.tif')
		for f in glob.glob(search_pattern):
			print(f)

	def do_whereami(self, arg):
		search_pattern = os.path.join(self.image_source, '*.png')
		all_images = glob.glob(search_pattern)
		if not all_images:
			print('No images')
			return
		latest_image = max(all_images, key=os.path.getctime)
		coordinates = locate_image(latest_image)
		print(coordinates)

	def do_exit(self, arg):
		return True

if __name__ == '__main__':
	CommandShell().cmdloop()
