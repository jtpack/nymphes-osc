from .ControlParameter_Modulated import ControlParameter_Modulated


class MixParams:
    """A class for tracking all of mix-related control parameters"""

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        self._osc = ControlParameter_Modulated(dispatcher=dispatcher,
                                               osc_send_function=osc_send_function,
                                               midi_send_function=midi_send_function,
                                               base_osc_address='/mix/osc',
                                               value_cc=9,
                                               mod_cc=32)

        self._sub = ControlParameter_Modulated(dispatcher=dispatcher,
                                               osc_send_function=osc_send_function,
                                               midi_send_function=midi_send_function,
                                               base_osc_address='/mix/sub',
                                               value_cc=10,
                                               mod_cc=33)

        self._noise = ControlParameter_Modulated(dispatcher=dispatcher,
                                                 osc_send_function=osc_send_function,
                                                 midi_send_function=midi_send_function,
                                                 base_osc_address='/mix/noise',
                                                 value_cc=11,
                                                 mod_cc=34)

    @property
    def osc(self):
        return self._osc

    @property
    def sub(self):
        return self._sub

    @property
    def noise(self):
        return self._noise

    def on_midi_message(self, midi_message):
        self.osc.on_midi_message(midi_message)
        self.sub.on_midi_message(midi_message)
        self.noise.on_midi_message(midi_message)

    def set_mod_source(self, mod_source):
        self.osc.set_mod_source(mod_source)
        self.sub.set_mod_source(mod_source)
        self.noise.set_mod_source(mod_source)
