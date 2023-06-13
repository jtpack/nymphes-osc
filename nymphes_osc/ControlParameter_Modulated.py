from pythonosc.osc_message_builder import OscMessageBuilder


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
        - osc_send_function is a function that we can call to send an outgoing OSC message (signature: f(osc_message))
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

        except ValueError:
            raise ValueError(f'value could not be converted to an int: {val}') from None

    @property
    def value_cc(self):
        return self._value_cc

    def on_osc_message(self, address, *args):
        # Get the new value and store it
        val = args[0]
        self.value = val

        print(f'{address}: {val}')

        # Send a MIDI message
        self._midi_send_function(midi_cc=self.value_cc, value=self.value)

    def on_midi_message(self, midi_message):
        # Determine whether this midi message matches our MIDI CC
        #
        if midi_message.is_cc():
            if midi_message.control == self.value_cc:
                # This is a MIDI Control Change message that matches our CC number.

                # Update our value
                self.value = midi_message.value

                # Build an OSC message
                osc_address = self._base_osc_address + "/value"
                msg = OscMessageBuilder(address=osc_address)
                msg.add_arg(self.value)
                msg = msg.build()

                # Send it
                self._osc_send_function(msg)

        # Also pass the message to our modulation amounts object
        self.mod.on_midi_message(midi_message)

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
                self._osc_send_function.send_message(self.base_osc_address + '/mod/lfo2', self._lfo2_value)

            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None

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
                self._osc_send_function.send_message(self.base_osc_address + '/mod/wheel', self._wheel_value)

            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None

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
                self._osc_send_function.send_message(self.base_osc_address + '/mod/velocity', self._velocity_value)

            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None

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
                self._osc_send_function.send_message(self.base_osc_address + '/mod/aftertouch', self._aftertouch_value)

            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None

        @property
        def mod_cc(self):
            return self._mod_cc

        def on_osc_lfo2_message(self, address, *args):
            val = args[0]
            self._lfo2_value = val
            print(f'{address}: {val}')

            # Send a MIDI message to the Nymphes to set the mod source to LFO2
            self._midi_send_function(midi_cc=30, value=0)

            # Send a MIDI message with the LFO2 modulation amount
            self._midi_send_function(midi_cc=self.mod_cc, value=self._lfo2_value)

        def on_osc_wheel_message(self, address, *args):
            val = args[0]
            self._wheel_value = val
            print(f'{address}: {val}')

            # Send a MIDI message to the Nymphes to set the mod source to Wheel
            self._midi_send_function(midi_cc=30, value=1)

            # Send a MIDI message with the LFO2 modulation amount
            self._midi_send_function(midi_cc=self.mod_cc, value=self._wheel_value)

        def on_osc_velocity_message(self, address, *args):
            val = args[0]
            self._velocity_value = val
            print(f'{address}: {val}')

            # Send a MIDI message to the Nymphes to set the mod source to Velocity
            self._midi_send_function(midi_cc=30, value=2)

            # Send a MIDI message with the Velocity modulation amount
            self._midi_send_function(midi_cc=self.mod_cc, value=self._velocity_value)

        def on_osc_aftertouch_message(self, address, *args):
            val = args[0]
            self._aftertouch_value = val
            print(f'{address}: {val}')

            # Send a MIDI message to the Nymphes to set the mod source to Aftertouch
            self._midi_send_function(midi_cc=30, value=3)

            # Send a MIDI message with the Aftertouch modulation amount
            self._midi_send_function(midi_cc=self.mod_cc, value=self._aftertouch_value)
            
        def on_midi_message(self, midi_message):
            # Determine whether we should respond to the MIDI message
    
            if midi_message.is_cc():
                
                if midi_message.control == 30:
                    # This is the modulation source control message.
                    # Store the new source.
                    self._curr_mod_source = midi_message.value

                elif midi_message.control == self.mod_cc:
                    # This is our modulation MIDI CC, so the message
                    # sets a modulation amount
                    
                    # Set the correct amount based on the current modulation source
                    if self._curr_mod_source == 0:
                        # Update the modulation amount
                        self._lfo2_value = midi_message.value

                        # Build an OSC message
                        msg = OscMessageBuilder(address=self.base_osc_address + "/mod/lfo2")
                        msg.add_arg(self._lfo2_value)
                        msg = msg.build()

                        # Send it
                        self._osc_send_function(msg)
                        
                    elif self._curr_mod_source == 1:
                        # Update the modulation amount
                        self._wheel_value = midi_message.value

                        # Build an OSC message
                        msg = OscMessageBuilder(address=self.base_osc_address + "/mod/wheel")
                        msg.add_arg(self._wheel_value)
                        msg = msg.build()

                        # Send it
                        self._osc_send_function(msg)
                        
                    elif self._curr_mod_source == 2:
                        # Update the modulation amount
                        self._velocity_value = midi_message.value

                        # Build an OSC message
                        msg = OscMessageBuilder(address=self.base_osc_address + "/mod/velocity")
                        msg.add_arg(self._velocity_value)
                        msg = msg.build()

                        # Send it
                        self._osc_send_function(msg)
                        
                    elif self._curr_mod_source == 3:
                        # Update the modulation amount
                        self._aftertouch_value = midi_message.value

                        # Build an OSC message
                        msg = OscMessageBuilder(address=self.base_osc_address + "/mod/aftertouch")
                        msg.add_arg(self._aftertouch_value)
                        msg = msg.build()

                        # Send it
                        self._osc_send_function(msg)
