from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
from ModulatedControlParameter import ModulatedControlParameter
from BasicControlParameter import BasicControlParameter


class MixParams:
    """A class for tracking all of mix-related control parameters"""

    def __init__(self, dispatcher, osc_client):
        self._osc = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/mix/osc')
        self._sub = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/mix/sub')
        self._noise = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/mix/noise')

    @property
    def osc(self):
        return self._osc

    @property
    def sub(self):
        return self._sub

    @property
    def noise(self):
        return self._noise
