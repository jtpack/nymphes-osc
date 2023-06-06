from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
from ModulatedControlParameter import ModulatedControlParameter
from BasicControlParameter import BasicControlParameter


class LpfParams:
    """A class for tracking all of LPF-related control parameters"""

    def __init__(self, dispatcher, osc_client):
        self._cutoff = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/lpf/cutoff')
        self._resonance = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/lpf/resonance')
        self._tracking = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/lpf/tracking')
        self._env_depth = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/lpf/env_depth')
        self._lfo1 = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/lpf/lfo1')

    @property
    def cutoff(self):
        return self._cutoff

    @property
    def resonance(self):
        return self._resonance

    @property
    def tracking(self):
        return self._tracking

    @property
    def env_depth(self):
        return self._env_depth

    @property
    def lfo1(self):
        return self._lfo1
