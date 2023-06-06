from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
from ModulatedControlParameter import ModulatedControlParameter
from BasicControlParameter import BasicControlParameter


class ReverbParams:
    """A class for tracking all control parameters related to reverb"""

    def __init__(self, dispatcher, osc_client):
        self._size = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/reverb/size')
        self._decay = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/reverb/decay')
        self._filter = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/reverb/filter')
        self._mix = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/reverb/mix')

    @property
    def size(self):
        return self._size

    @property
    def decay(self):
        return self._decay

    @property
    def filter(self):
        return self._filter

    @property
    def mix(self):
        return self._mix

