from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
from ModulatedControlParameter import ModulatedControlParameter
from BasicControlParameter import BasicControlParameter


class HpfParams:
    """A class for tracking all of HPF-related control parameters"""

    def __init__(self, dispatcher, osc_client):
        self._cutoff = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/hpf/cutoff')

    @property
    def cutoff(self):
        return self._cutoff
