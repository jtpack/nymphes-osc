from nymphes_osc.ControlParameter_Basic import ControlParameter_Basic


class ControlParameter_ModSource(ControlParameter_Basic):
    """
    Control parameter for Mod Source Selector, which has four possible settings.
    These can be set using either their int values or string names.
    0 = 'lfo2'
    1 = 'wheel'
    2 = 'velocity'
    3 = 'aftertouch'
    """

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        super().__init__(dispatcher,
                         osc_send_function=osc_send_function,
                         midi_send_function=midi_send_function,
                         osc_address='/mod_source',
                         midi_cc=30,
                         min_val=0,
                         max_val=3)
        
    @property
    def string_value(self):
        if self.value == 0:
            return 'lfo2'
        elif self.value == 1:
            return 'wheel'
        elif self.value == 2:
            return 'velocity'
        elif self.value == 3:
            return 'aftertouch'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self.value}')
        
    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'lfo2':
            self.value = 0
        elif string_val == 'wheel':
            self.value = 1
        elif string_val == 'velocity':
            self.value = 2
        elif string_val == 'aftertouch':
            self.value = 3
        else:
            raise Exception(f'Invalid string_value: {string_val}')
