from .ControlParameter_Modulated import ControlParameter_Modulated
from .ControlParameter_Basic import ControlParameter_Basic


class AmpParams:
    """A class for tracking all of amplitude-related control parameters"""

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        self._attack = ControlParameter_Modulated(dispatcher=dispatcher,
                                                  osc_send_function=osc_send_function,
                                                  midi_send_function=midi_send_function,
                                                  base_osc_address='/amp/attack',
                                                  value_cc=73,
                                                  mod_cc=52)

        self._decay = ControlParameter_Modulated(dispatcher=dispatcher,
                                                 osc_send_function=osc_send_function,
                                                 midi_send_function=midi_send_function,
                                                 base_osc_address='/amp/decay',
                                                 value_cc=84,
                                                 mod_cc=53)

        self._sustain = ControlParameter_Modulated(dispatcher=dispatcher,
                                                   osc_send_function=osc_send_function,
                                                   midi_send_function=midi_send_function,
                                                   base_osc_address='/amp/sustain',
                                                   value_cc=85,
                                                   mod_cc=54)

        self._release = ControlParameter_Modulated(dispatcher=dispatcher,
                                                   osc_send_function=osc_send_function,
                                                   midi_send_function=midi_send_function,
                                                   base_osc_address='/amp/release',
                                                   value_cc=72,
                                                   mod_cc=55)

        self._level = ControlParameter_Basic(dispatcher=dispatcher,
                                             osc_send_function=osc_send_function,
                                             midi_send_function=midi_send_function,
                                             osc_address='/amp/level/value',
                                             midi_cc=7,
                                             min_val=0,
                                             max_val=127)

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

    @property
    def level(self):
        return self._level

    def on_midi_message(self, midi_message):
        if self.attack.on_midi_message(midi_message):
            return True
        if self.decay.on_midi_message(midi_message):
            return True
        if self.sustain.on_midi_message(midi_message):
            return True
        if self.release.on_midi_message(midi_message):
            return True
        if self.level.on_midi_message(midi_message):
            return True

        return False

    def set_mod_source(self, mod_source):
        self.attack.set_mod_source(mod_source)
        self.decay.set_mod_source(mod_source)
        self.sustain.set_mod_source(mod_source)
        self.release.set_mod_source(mod_source)
