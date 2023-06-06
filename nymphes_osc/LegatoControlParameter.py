from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
from ModulatedControlParameter import ModulatedControlParameter
from BasicControlParameter import BasicControlParameter


class LegatoControlParameter(BasicControlParameter):
    """
    Control parameter for Legato, which has two possible settings. These can be set using their int values, string names, or True and False.
    0 = 'off'
    1 = 'on'
    """

    def __init__(self, dispatcher, osc_client):
        super().__init__(dispatcher, osc_client, osc_address='/legato', min_val=0, max_val=1)

    @property
    def string_value(self):
        if self.value == 0:
            return 'off'
        elif self.value == 1:
            return 'on'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self.value}')

    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'off':
            self.value = 0
        elif string_val == 'on':
            self.value = 1
        else:
            raise Exception(f'Invalid string_value: {string_val}')
