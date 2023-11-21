from nymphes_osc.src.parameter_classes.ControlParameter_Modulated import ControlParameter_Modulated
from nymphes_osc.src.parameter_classes.ControlParameter_LfoType import ControlParameter_LfoType
from nymphes_osc.src.parameter_classes.ControlParameter_LfoKeySync import ControlParameter_LfoKeySync


class Lfo1Params:
    """A class for tracking all control parameters related to the pitch/filter LFO (lfo1)"""

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        self._rate = ControlParameter_Modulated(dispatcher=dispatcher,
                                                osc_send_function=osc_send_function,
                                                midi_send_function=midi_send_function,
                                                base_osc_address='/lfo1/rate',
                                                value_cc=18,
                                                mod_cc=56)

        self._wave = ControlParameter_Modulated(dispatcher=dispatcher,
                                                osc_send_function=osc_send_function,
                                                midi_send_function=midi_send_function,
                                                base_osc_address='/lfo1/wave',
                                                value_cc=19,
                                                mod_cc=57)

        self._delay = ControlParameter_Modulated(dispatcher=dispatcher,
                                                 osc_send_function=osc_send_function,
                                                 midi_send_function=midi_send_function,
                                                 base_osc_address='/lfo1/delay',
                                                 value_cc=20,
                                                 mod_cc=58)

        self._fade = ControlParameter_Modulated(dispatcher=dispatcher,
                                                osc_send_function=osc_send_function,
                                                midi_send_function=midi_send_function,
                                                base_osc_address='/lfo1/fade',
                                                value_cc=21,
                                                mod_cc=59)

        self._type = ControlParameter_LfoType(dispatcher=dispatcher,
                                              osc_send_function=osc_send_function,
                                              midi_send_function=midi_send_function,
                                              osc_address='/lfo1/type',
                                              midi_cc=22)

        self._key_sync = ControlParameter_LfoKeySync(dispatcher=dispatcher,
                                                     osc_send_function=osc_send_function,
                                                     midi_send_function=midi_send_function,
                                                     osc_address='/lfo1/key_sync',
                                                     midi_cc=23)

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
        if self.rate.on_midi_message(midi_message):
            return True
        if self.wave.on_midi_message(midi_message):
            return True
        if self.delay.on_midi_message(midi_message):
            return True
        if self.fade.on_midi_message(midi_message):
            return True
        if self.type.on_midi_message(midi_message):
            return True
        if self.key_sync.on_midi_message(midi_message):
            return True

        return False

    def set_mod_source(self, mod_source):
        self.rate.set_mod_source(mod_source)
        self.wave.set_mod_source(mod_source)
        self.delay.set_mod_source(mod_source)
        self.fade.set_mod_source(mod_source)
