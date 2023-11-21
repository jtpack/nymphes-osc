from nymphes_osc.src.parameter_classes.ControlParameter_Modulated import ControlParameter_Modulated


class HpfParams:
    """A class for tracking all of HPF-related control parameters"""

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        self._cutoff = ControlParameter_Modulated(dispatcher=dispatcher,
                                                  osc_send_function=osc_send_function,
                                                  midi_send_function=midi_send_function,
                                                  base_osc_address='/hpf/cutoff',
                                                  value_cc=81,
                                                  mod_cc=45)

    @property
    def cutoff(self):
        return self._cutoff

    def on_midi_message(self, midi_message):
        if self.cutoff.on_midi_message(midi_message):
            return True

        return False

    def set_mod_source(self, mod_source):
        self.cutoff.set_mod_source(mod_source)
