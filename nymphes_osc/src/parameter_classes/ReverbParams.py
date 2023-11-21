from nymphes_osc.src.parameter_classes.ControlParameter_Modulated import ControlParameter_Modulated


class ReverbParams:
    """A class for tracking all control parameters related to reverb"""

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        self._size = ControlParameter_Modulated(dispatcher=dispatcher,
                                                osc_send_function=osc_send_function,
                                                midi_send_function=midi_send_function,
                                                base_osc_address='/reverb/size',
                                                value_cc=75,
                                                mod_cc=86)

        self._decay = ControlParameter_Modulated(dispatcher=dispatcher,
                                                 osc_send_function=osc_send_function,
                                                 midi_send_function=midi_send_function,
                                                 base_osc_address='/reverb/decay',
                                                 value_cc=76,
                                                 mod_cc=87)

        self._filter = ControlParameter_Modulated(dispatcher=dispatcher,
                                                  osc_send_function=osc_send_function,
                                                  midi_send_function=midi_send_function,
                                                  base_osc_address='/reverb/filter',
                                                  value_cc=77,
                                                  mod_cc=88)

        self._mix = ControlParameter_Modulated(dispatcher=dispatcher,
                                               osc_send_function=osc_send_function,
                                               midi_send_function=midi_send_function,
                                               base_osc_address='/reverb/mix',
                                               value_cc=78,
                                               mod_cc=89)

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

    def on_midi_message(self, midi_message):
        if self.size.on_midi_message(midi_message):
            return True
        if self.decay.on_midi_message(midi_message):
            return True
        if self.filter.on_midi_message(midi_message):
            return True
        if self.mix.on_midi_message(midi_message):
            return True

        return False

    def set_mod_source(self, mod_source):
        self.size.set_mod_source(mod_source)
        self.decay.set_mod_source(mod_source)
        self.filter.set_mod_source(mod_source)
        self.mix.set_mod_source(mod_source)
