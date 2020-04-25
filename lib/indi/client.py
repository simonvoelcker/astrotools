import subprocess
import math
import re


class INDIClient:
    PROPERTY_RX = re.compile(r'(?P<device>.*)\.(?P<property>.*)\.(?P<element>.*)=(?P<value>.*)')

    def __init__(self, host='localhost', port=7624):
        self._host = host
        self._port = port

    def get_properties(self, device='*', property='*', element='*'):
        prop_name = f'{device}.{property}.{element}'
        _, process_output = self._run_cmd('indi_getprop', [prop_name])
        properties = process_output.decode('utf-8').split('\n')
        return self._parse_properties(properties)

    def set_property(self, device, property, element, value):
        prop_assignment = f'{device}.{property}.{element}={value}'
        self._run_cmd('indi_setprop', [prop_assignment])

    def set_property_sync(self, device, property, element, value, timeout=2):
        self.set_property(device, property, element, value)
        self._run_cmd('indi_eval', ['-w', '-t', str(math.ceil(timeout)), f'"{device}.{property}._STATE"==1'])

    def _run_cmd(self, cmd, args):
        full_args = [cmd, '-h', self._host, '-p', str(self._port)] + args
        process = subprocess.Popen(full_args, stdout=subprocess.PIPE)
        data = process.communicate()
        return process.returncode, data[0]

    def _parse_properties(self, properties):
        return [self._parse_property(prop) for prop in properties if prop]

    def _parse_property(self, line):
        return self.PROPERTY_RX.match(line).groupdict()
