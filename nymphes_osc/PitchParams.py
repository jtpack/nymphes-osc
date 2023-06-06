from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
from ModulatedControlParameter import ModulatedControlParameter
from BasicControlParameter import BasicControlParameter


class PitchParams:
    """A class for tracking all of pitch-related control parameters"""

    def __init__(self, dispatcher, osc_client):
        self._detune = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function,
                                                           '/pitch/detune')
        self._chord = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function,
                                                          '/pitch/chord')
        self._env_depth = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function,
                                                              '/pitch/env_depth')
        self._lfo1 = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function,
                                                         '/pitch/lfo1')
        self._glide = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function,
                                                          '/pitch/glide')

    @property
    def detune(self):
        return self._detune

    @property
    def chord(self):
        return self._chord

    @property
    def env_depth(self):
        return self._env_depth

    @property
    def lfo1(self):
        return self._lfo1

    @property
    def glide(self):
        return self._glide
