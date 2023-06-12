from nymphes_osc.ControlParameter_Modulated import ControlParameter_Modulated


class OscillatorParams:
    """A class for tracking all of the control parameters for the oscillator"""

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        self._wave = ControlParameter_Modulated(dispatcher=dispatcher,
                                                osc_send_function=osc_send_function,
                                                midi_send_function=midi_send_function,
                                                base_osc_address='/osc/wave',
                                                value_cc=70,
                                                mod_cc=31)

        self._pulsewidth = self._wave = ControlParameter_Modulated(dispatcher=dispatcher,
                                                                   osc_send_function=osc_send_function,
                                                                   midi_send_function=midi_send_function,
                                                                   base_osc_address='/osc/pulsewidth',
                                                                   value_cc=12,
                                                                   mod_cc=36)

    @property
    def wave(self):
        return self._wave

    @property
    def pulsewidth(self):
        return self._pulsewidth

    def on_midi_message(self, midi_message):
        self.wave.on_midi_message(midi_message)
        self.pulsewidth.on_midi_message(midi_message)
