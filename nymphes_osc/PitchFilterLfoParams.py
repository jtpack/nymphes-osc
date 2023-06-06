from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
from ModulatedControlParameter import ModulatedControlParameter
from BasicControlParameter import BasicControlParameter


class PitchFilterLfoParams:
    """A class for tracking all control parameters related to the pitch/filter LFO (lfo1)"""

    def __init__(self, dispatcher, osc_client):
        self._rate = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/lfo1/rate')
        self._wave = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/lfo1/wave')
        self._delay = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/lfo1/delay')
        self._fade = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/lfo1/fade')
        self._type = NymphesOscLfoTypeParameter(dispatcher, osc_client, '/lfo1/type/value')
        self._key_sync = NymphesOscLfoKeySyncParameter(dispatcher, osc_client, '/lfo1/key_sync/value')

    @property
    def rate(self):
        return self._rate

    @property
    def wave(self):
        return self._wave

    @property
    def delay(self):
        return self._delay

    @property
    def fade(self):
        return self._fade

    @property
    def type(self):
        return self._type

    @property
    def key_sync(self):
        return self._key_sync
