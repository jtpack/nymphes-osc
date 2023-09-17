from .ControlParameter_Basic import ControlParameter_Basic


class ControlParameter_Legato(ControlParameter_Basic):
    """
    Control parameter for Legato, which has two possible settings.
    These can be set using their int values, string names, or True and False.
    0 = 'off'
    127 = 'on'
    """

    def __init__(self, dispatcher, osc_send_function, midi_send_function):
        super().__init__(dispatcher,
                         osc_send_function=osc_send_function,
                         midi_send_function=midi_send_function,
                         osc_address='/legato',
                         midi_cc=68,
                         min_val=0,
                         max_val=127)

    @property
    def string_value(self):
        if self.value == 0:
            return 'off'
        elif self.value == 127:
            return 'on'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self.value}')

    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'off':
            self.value = 0
        elif string_val == 'on':
            self.value = 127
        else:
            raise Exception(f'Invalid string_value: {string_val}')
