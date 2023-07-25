from pythonosc.osc_message_builder import OscMessageBuilder
import time


class ControlParameter_Basic:
    """
    A control parameter in the Nymphes synthesizer that cannot be modulated by the modulation matrix.
    It has only one property: value.
    Its range is 0 to 127.
    """

    def __init__(self, dispatcher, osc_send_function, midi_send_function, osc_address, midi_cc, min_val=0, max_val=127):
        """
        - dispatcher is an OSC dispatcher that we use to map incoming OSC messages with our OSC addresses.
        - osc_send_function is a function that we can call to send an outgoing OSC message (signature: f(osc_message))
        - midi_send_function is a function that we can call to send an outgoing MIDI message (signature: f(midi_cc, value))
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

        # For filtering out duplicate messages
        self._last_midi_message_time = None
        self._last_osc_message_time = None

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
        # print(f'{address}: {args[0]}')

        # Get the new value
        value = args[0]

        # Ignore duplicate messages - these are messages with the
        # value as our current value, arriving within one second
        if value == self.value:
            if self._last_osc_message_time is not None:
                if time.perf_counter() - self._last_osc_message_time <= 1.0:
                    # This is a duplicate message.

                    # Update the time
                    self._last_osc_message_time = time.perf_counter()

                    # Do nothing else with this message
                    return

        # This is not a duplicate message, so handle it
        #

        # Store the new value
        self.value = value

        # Store the time
        self._last_osc_message_time = time.perf_counter()

        # Send a MIDI message
        self._midi_send_function(midi_cc=self.midi_cc, value=self.value)

    def on_midi_message(self, midi_message):
        """
        If midi_message is intended for us, then handle it and then
        return True.
        If not, then return False.
        """
        # Determine whether this midi message matches our MIDI CC
        #

        if midi_message.control == self.midi_cc:
            # This is a MIDI Control Change message that matches our CC number.

            # Ignore duplicate messages - these are messages with the
            # value as our current value, arriving within one second
            if midi_message.value == self.value:
                if self._last_midi_message_time is not None:
                    if time.perf_counter() - self._last_midi_message_time <= 1.0:
                        # This is a duplicate message.

                        # Update the time
                        self._last_midi_message_time = time.perf_counter()

                        # Do nothing else with this message
                        return

            # This is not a duplicate message, so handle it
            #

            # Update our value
            self.value = midi_message.value

            # Store the time
            self._last_midi_message_time = time.perf_counter()

            # Build an OSC message
            msg = OscMessageBuilder(address=self.osc_address)
            msg.add_arg(self.value)
            msg = msg.build()

            # Send it
            self._osc_send_function(msg)

            return True

        else:
            return False
