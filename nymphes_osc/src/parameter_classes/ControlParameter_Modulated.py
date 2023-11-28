from pythonosc.osc_message_builder import OscMessageBuilder
import time


class ControlParameter_Modulated:
    """
    A control parameter in the Nymphes synthesizer that can be modulated with the modulation matrix.
    There are the following values:
    - Value
    - LFO2 Modulation Amount
    - Mod Wheel Modulation Amount
    - Velocity Modulation Amount
    - Aftertouch Modulation Amount

    All properties are MIDI-controlled on the Nymphes, so they have a range of 0 to 127
    """

    def __init__(self, dispatcher, osc_send_function, midi_send_function, base_osc_address, value_cc, mod_cc):
        """
        - dispatcher is an OSC dispatcher that we use to map incoming OSC messages with our OSC addresses.
        - osc_send_function is a function that we can call to send an outgoing OSC message (signature: f(address, *args))
        - midi_send_function is a function that we can call to send an outgoing MIDI message (signature: f(midi_cc, value))
        - base_osc_address is a string. THe full OSC address for each of the values is built with the base OSC address
        as a starting point. Ex: /base_osc_address/value, /base_osc_address/mod/lfo2, etc
        - value_cc, mod_cc are the MIDI CC numbers used for each value
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

        # Validate base_osc_address
        if base_osc_address is None:
            raise Exception('base_osc_address is None')
        else:
            self._base_osc_address = base_osc_address

        # Validate value_cc
        if (value_cc < 0) or (value_cc > 127):
            raise Exception(f'Invalid value_cc: {value_cc}')
        else:
            self._value_cc = value_cc

        # Validate mod_cc
        if (mod_cc < 0) or (mod_cc > 127):
            raise Exception(f'Invalid mod_cc: {mod_cc}')

        self._value = 0

        # Create the modulation amounts object
        self.mod = self.ModulationAmounts(dispatcher, osc_send_function, midi_send_function,
                                          self._base_osc_address, mod_cc)

        # Map value OSC address
        dispatcher.map(self._base_osc_address + '/value', self.on_osc_message)

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
            if new_val < 0 or new_val > 127:
                raise Exception(f'Invalid value: {new_val}')

            # Store the new value
            self._value = new_val

            # Send an OSC message
            self._osc_send_function(self._base_osc_address + "/value", self.value)

        except ValueError:
            raise ValueError(f'value could not be converted to an int: {val}') from None

    @property
    def float_value(self):
        return float(self.value / 127.0)

    @property
    def value_cc(self):
        return self._value_cc

    def on_osc_message(self, address, *args):
        # Get the new value and store it
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

        self.value = value

        # Store the time
        self._last_osc_message_time = time.perf_counter()

        # print(f'{address}: {value}')

        # Send a MIDI message
        self._midi_send_function(midi_cc=self.value_cc, value=self.value)

    def on_midi_message(self, midi_message):
        """
        If midi_message is intended for us, then handle it and then
        return True.
        If not, then return False.
        """

        # Determine whether this midi message matches our MIDI CC
        #
        if midi_message.control == self.value_cc:
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
                        return True

            # This is not a duplicate message, so handle it
            #

            # Update our value and trigger OSC message
            self.value = midi_message.value

            # Store the time
            self._last_midi_message_time = time.perf_counter()

            return True
        else:
            # Pass the message to our modulation amounts object
            return self.mod.on_midi_message(midi_message)

    def set_mod_source(self, mod_source):
        self.mod.set_mod_source(mod_source)

    class ModulationAmounts:
        def __init__(self, dispatcher, osc_send_function, midi_send_function, base_osc_address, mod_cc):

            self._lfo2_value = 0
            self._wheel_value = 0
            self._velocity_value = 0
            self._aftertouch_value = 0

            self.base_osc_address = base_osc_address

            # Register for incoming OSC messages
            dispatcher.map(self.base_osc_address + '/mod/lfo2', self.on_osc_lfo2_message)
            dispatcher.map(self.base_osc_address + '/mod/wheel', self.on_osc_wheel_message)
            dispatcher.map(self.base_osc_address + '/mod/velocity', self.on_osc_velocity_message)
            dispatcher.map(self.base_osc_address + '/mod/aftertouch', self.on_osc_aftertouch_message)

            # Store the OSC send function for when we need to send out OSC messages
            self._osc_send_function = osc_send_function

            # Store MIDI send function for when we need to send out MIDI messages
            self._midi_send_function = midi_send_function

            # Store the MIDI CC numbers for each modulation type
            self._mod_cc = mod_cc

            # Keep track of the current modulation source as MIDI CC# 30 messages are
            # received
            self._curr_mod_source = 0

        @property
        def lfo2(self):
            return self._lfo2_value

        @lfo2.setter
        def lfo2(self, value):
            try:
                # Convert value to an integer
                new_val = int(value)

                # Validate the value
                if new_val < 0 or new_val > 127:
                    raise Exception(f'Invalid value: {new_val}')

                # Store the new value
                self._lfo2_value = new_val

                # Send out an OSC message with the new value
                self._osc_send_function(self.base_osc_address + '/mod/lfo2', self.lfo2)

            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None

        @property
        def lfo2_float_value(self):
            return float(self.lfo2 / 127.0)
        
        @property
        def wheel(self):
            return self._wheel_value

        @wheel.setter
        def wheel(self, value):
            try:
                # Convert value to an integer
                new_val = int(value)

                # Validate the value
                if new_val < 0 or new_val > 127:
                    raise Exception(f'Invalid value: {new_val}')

                # Store the new value
                self._wheel_value = new_val

                # Send out an OSC message with the new value
                self._osc_send_function(self.base_osc_address + '/mod/wheel', self.wheel)

            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None

        @property
        def wheel_float_value(self):
            return float(self.wheel / 127.0)

        @property
        def velocity(self):
            return self._velocity_value

        @velocity.setter
        def velocity(self, value):
            try:
                # Convert value to an integer
                new_val = int(value)

                # Validate the value
                if new_val < 0 or new_val > 127:
                    raise Exception(f'Invalid value: {new_val}')

                # Store the new value
                self._velocity_value = new_val

                # Send out an OSC message with the new value
                self._osc_send_function(self.base_osc_address + '/mod/velocity', self.velocity)

            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None

        @property
        def velocity_float_value(self):
            return float(self.velocity / 127.0)
        
        @property
        def aftertouch(self):
            return self._aftertouch_value

        @aftertouch.setter
        def aftertouch(self, value):
            try:
                # Convert value to an integer
                new_val = int(value)

                # Validate the value
                if new_val < 0 or new_val > 127:
                    raise Exception(f'Invalid value: {new_val}')

                # Store the new value
                self._aftertouch_value = new_val

                # Send out an OSC message with the new value
                self._osc_send_function(self.base_osc_address + '/mod/aftertouch', self.aftertouch)

            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None

        @property
        def aftertouch_float_value(self):
            return float(self.aftertouch / 127.0)

        @property
        def mod_cc(self):
            return self._mod_cc

        def on_osc_lfo2_message(self, address, *args):
            val = args[0]

            # Update the protected variable so we don't trigger a new osc message
            self._lfo2_value = val

            # Send a MIDI message to the Nymphes to set the mod source to LFO2
            self._midi_send_function(midi_cc=30, value=0)

            # Send a MIDI message with the LFO2 modulation amount
            self._midi_send_function(midi_cc=self.mod_cc, value=self.lfo2)

        def on_osc_wheel_message(self, address, *args):
            val = args[0]

            # Update the protected variable so we don't trigger a new OSC message
            self._wheel_value = val

            # Send a MIDI message to the Nymphes to set the mod source to Wheel
            self._midi_send_function(midi_cc=30, value=1)

            # Send a MIDI message with the LFO2 modulation amount
            self._midi_send_function(midi_cc=self.mod_cc, value=self.wheel)

        def on_osc_velocity_message(self, address, *args):
            val = args[0]

            # Update the protected variable so we don't trigger an OSC message
            self._velocity_value = val

            # Send a MIDI message to the Nymphes to set the mod source to Velocity
            self._midi_send_function(midi_cc=30, value=2)

            # Send a MIDI message with the Velocity modulation amount
            self._midi_send_function(midi_cc=self.mod_cc, value=self.velocity)

        def on_osc_aftertouch_message(self, address, *args):
            val = args[0]

            # Update the protected variable so we don't trigger an OSC message
            self._aftertouch_value = val

            # Send a MIDI message to the Nymphes to set the mod source to Aftertouch
            self._midi_send_function(midi_cc=30, value=3)

            # Send a MIDI message with the Aftertouch modulation amount
            self._midi_send_function(midi_cc=self.mod_cc, value=self.aftertouch)
            
        def on_midi_message(self, midi_message):
            # Determine whether we should respond to the MIDI message

            if midi_message.control == self.mod_cc:
                # This is our modulation MIDI CC, so the message
                # sets a modulation amount

                # Set the correct amount based on the current modulation source
                if self._curr_mod_source == 0:
                    # Update the modulation amount and trigger an OSC message
                    self.lfo2 = midi_message.value

                elif self._curr_mod_source == 1:
                    # Update the modulation amount and trigger an OSC message
                    self.wheel = midi_message.value

                elif self._curr_mod_source == 2:
                    # Update the modulation amount and trigger an OSC message
                    self.velocity = midi_message.value

                elif self._curr_mod_source == 3:
                    # Update the modulation amount and trigger an OSC message
                    self.aftertouch = midi_message.value

                return True

            else:
                # midi_message did not match our cc number
                return False

        def set_mod_source(self, mod_source):
            self._curr_mod_source = mod_source
