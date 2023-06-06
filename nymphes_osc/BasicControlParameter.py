from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido

class BasicControlParameter:
    """
    A control parameter in the Nymphes synthesizer that cannot be modulated by the modulation matrix.
    It has only one property: value.
    Its range is 0 to 127.
    """

    def __init__(self, dispatcher, osc_send_function, midi_send_function, osc_address, midi_cc, min_val=0, max_val=127):
        """
        dispatcher is an OSC dispatcher object.
        osc_send_function is a function that we can call to send an outgoing OSC message (signature: f(osc_message))
        midi_send_function is a function that we can call to send an outgoing MIDI message (signature: f(midi_cc, value))
        """
        
        # Validate osc_send_function
        if osc_send_function is None:
            raise Exception('osc_send_function is None')
        else:
            self._osc_send_function = osc_send_function

        # Validate midi_send_function
        if midi_send_function is None:
            raise Exception('midi_send_function is None')
        else:
            self._midi_send_function = midi_send_function

        # Validate osc_address
        if osc_address is None:
            raise Exception('osc_address is None')
        else:
            self._osc_address = osc_address

        # Validate midi_cc
        if (midi_cc < 0) or (midi_cc > 127):
            raise Exception(f'Invalid midi_cc: {midi_cc}')
        else:
            self._midi_cc = midi_cc

        # Validate min_val
        if (min_val < 0) or (min_val > 127):
            raise Exception(f'Invalid min_val: {min_val}')
        else:
            self._min_val = min_val

        # Validate max_val
        if (max_val < 0) or (max_val > 127):
            raise Exception(f'Invalid max_val: {max_val}')
        else:
            self._max_val = max_val

        self._value = 0
        
        # Register for OSC messages
        dispatcher.map(self._osc_address, self.on_osc_message)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        try:
            # Convert value to an integer
            new_val = int(val)

            # Validate the value
            if new_val < self.min_val or new_val > self._max_val:
                raise Exception(f'Value {new_val} must be within {self.min_val} and {self._max_val}')

            # Store the new value
            self._value = new_val

            # Send out an OSC message with the new value
            self._osc_client.send_message(self._osc_address, self._value)

        except ValueError:
            raise ValueError(f'value could not be converted to an int: {val}') from None

    @property
    def min_val(self):
        return self._min_val

    @property
    def max_val(self):
        return self._max_val

    @property
    def midi_cc(self):
        return self._midi_cc

    @property
    def osc_address(self):
        return self._osc_address

    def on_osc_message(self, address, *args):
        # Get the new value
        val = args[0]

        # Set _value, our private variable, rather than using the setter,
        # as we don't want to trigger an outgoing OSC message
        self._value = val

        print(f'{address}: {val}')

        # Send a MIDI message
        self._midi_send_function(midi_cc=self.midi_cc, value=self.value)
