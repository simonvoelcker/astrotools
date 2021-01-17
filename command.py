import cmd

from hti.server.axes.axis_control import AxisControl


class CommandShell(cmd.Cmd):
	intro = 'Interactive command shell for axis control'
	prompt = '>>> '

	axis_control = AxisControl()

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
		self.axis_control.set_axis_speeds(ra_dps=0.0, dec_dps=0.0)

	def do_ra(self, arg):
		print(f'Setting RA axis speed to {float(arg)}')
		self.axis_control.set_axis_speeds(ra_dps=float(arg))

	def do_dec(self, arg):
		print(f'Setting DEC axis speed to {float(arg)}')
		self.axis_control.set_axis_speeds(dec_dps=float(arg))


if __name__ == '__main__':
	CommandShell().cmdloop()
