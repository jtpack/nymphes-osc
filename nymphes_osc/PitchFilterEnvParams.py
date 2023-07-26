from .ControlParameter_Modulated import ControlParameter_Modulated


class PitchFilterEnvParams:
    """A class for tracking all control parameters related to the pitch/filter envelope generator"""

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        self._attack = ControlParameter_Modulated(dispatcher=dispatcher,
                                                  osc_send_function=osc_send_function,
                                                  midi_send_function=midi_send_function,
                                                  base_osc_address='/pitch_filter_env/attack',
                                                  value_cc=79,
                                                  mod_cc=48)

        self._decay = ControlParameter_Modulated(dispatcher=dispatcher,
                                                 osc_send_function=osc_send_function,
                                                 midi_send_function=midi_send_function,
                                                 base_osc_address='/pitch_filter_env/decay',
                                                 value_cc=80,
                                                 mod_cc=49)

        self._sustain = ControlParameter_Modulated(dispatcher=dispatcher,
                                                   osc_send_function=osc_send_function,
                                                   midi_send_function=midi_send_function,
                                                   base_osc_address='/pitch_filter_env/sustain',
                                                   value_cc=82,
                                                   mod_cc=50)

        self._release = ControlParameter_Modulated(dispatcher=dispatcher,
                                                   osc_send_function=osc_send_function,
                                                   midi_send_function=midi_send_function,
                                                   base_osc_address='/pitch_filter_env/release',
                                                   value_cc=83,
                                                   mod_cc=51)

    @property
    def attack(self):
        return self._attack

    @property
    def decay(self):
        return self._decay

    @property
    def sustain(self):
        return self._sustain

    @property
    def release(self):
        return self._release

    def on_midi_message(self, midi_message):
        if self.attack.on_midi_message(midi_message):
            return True
        if self.decay.on_midi_message(midi_message):
            return True
        if self.sustain.on_midi_message(midi_message):
            return True
        if self.release.on_midi_message(midi_message):
            return True

        return False

    def set_mod_source(self, mod_source):
        self.attack.set_mod_source(mod_source)
        self.decay.set_mod_source(mod_source)
        self.sustain.set_mod_source(mod_source)
        self.release.set_mod_source(mod_source)
