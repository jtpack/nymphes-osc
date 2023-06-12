from nymphes_osc.ControlParameter_Basic import ControlParameter_Basic


class ControlParameter_LfoType(ControlParameter_Basic):
    """
    Control parameter for LFO type, which has four possible settings.
    These can be set using either their int values or string names.
    0 = 'bpm'
    1 = 'low'
    2 = 'high'
    3 = 'track'
    """

    def __init__(self, dispatcher, osc_send_function, midi_send_function, osc_address, midi_cc):
        super().__init__(dispatcher,
                         osc_send_function=osc_send_function,
                         midi_send_function=midi_send_function,
                         osc_address=osc_address,
                         midi_cc=midi_cc,
                         min_val=0,
                         max_val=3)

    @property
    def string_value(self):
        if self.value == 0:
            return 'bpm'
        elif self.value == 1:
            return 'low'
        elif self.value == 2:
            return 'high'
        elif self.value == 3:
            return 'track'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self.value}')

    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'bpm':
            self.value = 0
        elif string_val == 'low':
            self.value = 1
        elif string_val == 'high':
            self.value = 2
        elif string_val == 'track':
            self.value = 3
        else:
            raise Exception(f'Invalid string_value: {string_val}')
