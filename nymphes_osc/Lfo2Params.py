from .ControlParameter_Modulated import ControlParameter_Modulated
from .ControlParameter_LfoType import ControlParameter_LfoType
from .ControlParameter_LfoKeySync import ControlParameter_LfoKeySync


class Lfo2Params:
    """A class for tracking all control parameters related to LFO2"""

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        self._rate = ControlParameter_Modulated(dispatcher=dispatcher,
                                                  osc_send_function=osc_send_function,
                                                  midi_send_function=midi_send_function,
                                                  base_osc_address='/lfo2/rate',
                                                  value_cc=24,
                                                  mod_cc=60)

        self._wave = ControlParameter_Modulated(dispatcher=dispatcher,
                                                  osc_send_function=osc_send_function,
                                                  midi_send_function=midi_send_function,
                                                  base_osc_address='/lfo2/wave',
                                                  value_cc=25,
                                                  mod_cc=61)

        self._delay = ControlParameter_Modulated(dispatcher=dispatcher,
                                                  osc_send_function=osc_send_function,
                                                  midi_send_function=midi_send_function,
                                                  base_osc_address='/lfo2/delay',
                                                  value_cc=26,
                                                  mod_cc=62)

        self._fade = ControlParameter_Modulated(dispatcher=dispatcher,
                                                  osc_send_function=osc_send_function,
                                                  midi_send_function=midi_send_function,
                                                  base_osc_address='/lfo2/fade',
                                                  value_cc=27,
                                                  mod_cc=63)

        self._type = ControlParameter_LfoType(dispatcher=dispatcher,
                                              osc_send_function=osc_send_function,
                                              midi_send_function=midi_send_function,
                                              osc_address='/lfo2/type',
                                              midi_cc=28)

        self._key_sync = ControlParameter_LfoKeySync(dispatcher=dispatcher,
                                                     osc_send_function=osc_send_function,
                                                     midi_send_function=midi_send_function,
                                                     osc_address='lfo2/key_sync',
                                                     midi_cc=29)

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

    def on_midi_message(self, midi_message):
        self.rate.on_midi_message(midi_message)
        self.wave.on_midi_message(midi_message)
        self.delay.on_midi_message(midi_message)
        self.fade.on_midi_message(midi_message)
        self.type.on_midi_message(midi_message)
        self.key_sync.on_midi_message(midi_message)
