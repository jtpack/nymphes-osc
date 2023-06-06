from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
from ModulatedControlParameter import ModulatedControlParameter
from BasicControlParameter import BasicControlParameter


class OscillatorParams:
    """A class for tracking all of the control parameters for the oscillator"""

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        self.test_param = BasicControlParameter(dispatcher, osc_send_function, midi_send_function,
                                                osc_address='/test', midi_cc=70)
        # self._wave = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/osc/wave')
        # self._pulsewidth = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function,
        #                                                        '/osc/pulsewidth')

    @property
    def wave(self):
        return self._wave

    @property
    def pulsewidth(self):
        return self._pulsewidth