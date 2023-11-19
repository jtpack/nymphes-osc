from .ControlParameter_Modulated import ControlParameter_Modulated


class PitchParams:
    """A class for tracking all of pitch-related control parameters"""

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        self._detune = ControlParameter_Modulated(dispatcher=dispatcher,
                                                  osc_send_function=osc_send_function,
                                                  midi_send_function=midi_send_function,
                                                  base_osc_address='/pitch/detune',
                                                  value_cc=15,
                                                  mod_cc=39)

        self._chord = ControlParameter_Modulated(dispatcher=dispatcher,
                                                 osc_send_function=osc_send_function,
                                                 midi_send_function=midi_send_function,
                                                 base_osc_address='/pitch/chord',
                                                 value_cc=16,
                                                 mod_cc=40)

        self._env_depth = ControlParameter_Modulated(dispatcher=dispatcher,
                                                     osc_send_function=osc_send_function,
                                                     midi_send_function=midi_send_function,
                                                     base_osc_address='/pitch/env_depth',
                                                     value_cc=14,
                                                     mod_cc=41)

        self._lfo1 = ControlParameter_Modulated(dispatcher=dispatcher,
                                                osc_send_function=osc_send_function,
                                                midi_send_function=midi_send_function,
                                                base_osc_address='/pitch/lfo1',
                                                value_cc=13,
                                                mod_cc=35)

        self._glide = ControlParameter_Modulated(dispatcher=dispatcher,
                                                 osc_send_function=osc_send_function,
                                                 midi_send_function=midi_send_function,
                                                 base_osc_address='/pitch/glide',
                                                 value_cc=5,
                                                 mod_cc=37)

    @property
    def detune(self):
        return self._detune

    @property
    def chord(self):
        return self._chord

    @property
    def env_depth(self):
        return self._env_depth

    @property
    def lfo1(self):
        return self._lfo1

    @property
    def glide(self):
        return self._glide

    def on_midi_message(self, midi_message):
        if self.detune.on_midi_message(midi_message):
            return True
        if self.chord.on_midi_message(midi_message):
            return True
        if self.env_depth.on_midi_message(midi_message):
            return True
        if self.lfo1.on_midi_message(midi_message):
            return True
        if self.glide.on_midi_message(midi_message):
            return True

        return False

    def set_mod_source(self, mod_source):
        self.detune.set_mod_source(mod_source)
        self.chord.set_mod_source(mod_source)
        self.env_depth.set_mod_source(mod_source)
        self.lfo1.set_mod_source(mod_source)
        self.glide.set_mod_source(mod_source)
