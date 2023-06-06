from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
from ModulatedControlParameter import ModulatedControlParameter
from BasicControlParameter import BasicControlParameter


class PitchFilterEnvParams:
    """A class for tracking all control parameters related to the pitch/filter envelope generator"""

    def __init__(self, dispatcher, osc_client):
        self._attack = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function,
                                                 '/pitch_filter_env/attack')
        self._decay = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function,
                                                '/pitch_filter_env/decay')
        self._sustain = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function,
                                                  '/pitch_filter_env/sustain')
        self._release = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function,
                                                  '/pitch_filter_env/release')

    @property
    def attack(self):
        return self._attack

    @property
    def decay(self):
        return self._decay

    @property
    def sustain(self):
        return self._sustain

    @property
    def release(self):
        return self._release
