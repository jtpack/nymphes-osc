from .ControlParameter_Basic import ControlParameter_Basic


class ControlParameter_LfoKeySync(ControlParameter_Basic):
    """
    Control parameter for LFO key sync, which has two possible settings.
    These can be set using either their int values or string names.
    0 = 'off'
    1 = 'on'
    """

    def __init__(self, dispatcher, osc_send_function, midi_send_function, osc_address, midi_cc):
        super().__init__(dispatcher,
                         osc_send_function=osc_send_function,
                         midi_send_function=midi_send_function,
                         osc_address=osc_address,
                         midi_cc=midi_cc,
                         min_val=0,
                         max_val=1)

    @property
    def string_value(self):
        if self.value == 0:
            return 'off'
        elif self.value == 1:
            return 'on'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self.value}')

    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'off':
            self.value = 0
        elif string_val == 'on':
            self.value = 1
        else:
            raise Exception(f'Invalid string_value: {string_val}')