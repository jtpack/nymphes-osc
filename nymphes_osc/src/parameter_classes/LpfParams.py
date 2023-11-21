from nymphes_osc.src.parameter_classes.ControlParameter_Modulated import ControlParameter_Modulated


class LpfParams:
    """A class for tracking all of LPF-related control parameters"""

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        self._cutoff = ControlParameter_Modulated(dispatcher=dispatcher,
                                                  osc_send_function=osc_send_function,
                                                  midi_send_function=midi_send_function,
                                                  base_osc_address='/lpf/cutoff',
                                                  value_cc=74,
                                                  mod_cc=42)

        self._resonance = ControlParameter_Modulated(dispatcher=dispatcher,
                                                     osc_send_function=osc_send_function,
                                                     midi_send_function=midi_send_function,
                                                     base_osc_address='/lpf/resonance',
                                                     value_cc=71,
                                                     mod_cc=43)

        self._tracking = ControlParameter_Modulated(dispatcher=dispatcher,
                                                    osc_send_function=osc_send_function,
                                                    midi_send_function=midi_send_function,
                                                    base_osc_address='/lpf/tracking',
                                                    value_cc=4,
                                                    mod_cc=46)

        self._env_depth = ControlParameter_Modulated(dispatcher=dispatcher,
                                                     osc_send_function=osc_send_function,
                                                     midi_send_function=midi_send_function,
                                                     base_osc_address='/lpf/env_depth',
                                                     value_cc=3,
                                                     mod_cc=44)

        self._lfo1 = ControlParameter_Modulated(dispatcher=dispatcher,
                                                osc_send_function=osc_send_function,
                                                midi_send_function=midi_send_function,
                                                base_osc_address='/lpf/lfo1',
                                                value_cc=8,
                                                mod_cc=47)

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

    def on_midi_message(self, midi_message):
        if self.cutoff.on_midi_message(midi_message):
            return True
        if self.resonance.on_midi_message(midi_message):
            return True
        if self.tracking.on_midi_message(midi_message):
            return True
        if self.env_depth.on_midi_message(midi_message):
            return True
        if self.lfo1.on_midi_message(midi_message):
            return True

        return False

    def set_mod_source(self, mod_source):
        self.cutoff.set_mod_source(mod_source)
        self.resonance.set_mod_source(mod_source)
        self.tracking.set_mod_source(mod_source)
        self.env_depth.set_mod_source(mod_source)
        self.lfo1.set_mod_source(mod_source)
