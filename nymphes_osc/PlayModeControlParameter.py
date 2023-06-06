from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
from ModulatedControlParameter import ModulatedControlParameter
from BasicControlParameter import BasicControlParameter


class PlayModeControlParameter(BasicControlParameter):
    """
    Control parameter for Play Mode, which has six possible values. These can be set using either their int values or string names.
    0 = 'polyphonic'
    1 = 'unison-6'
    2 = 'unison-4'
    3 = 'triphonic'
    4 = 'duophonic'
    5 - 'monophonic'
    """

    def __init__(self, dispatcher, osc_client):
        super().__init__(dispatcher, osc_client, osc_address='/play_mode', min_val=0, max_val=5)

    @property
    def string_value(self):
        if self.value == 0:
            return 'polyphonic'
        elif self.value == 1:
            return 'unison-6'
        elif self.value == 2:
            return 'unison-4'
        elif self.value == 3:
            return 'triphonic'
        elif self.value == 4:
            return 'duophonic'
        elif self.value == 5:
            return 'monophonic'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self.value}')

    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'polyphonic':
            self.value = 0
        elif string_val == 'unison-6':
            self.value = 1
        elif string_val == 'unison-4':
            self.value = 2
        elif string_val == 'triphonic':
            self.value = 3
        elif string_val == 'duophonic':
            self.value = 2
        elif string_val == 'monophonic':
            self.value = 1
        else:
            raise Exception(f'Invalid string_value: {string_val}')

