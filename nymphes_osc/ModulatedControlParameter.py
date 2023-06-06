from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido


class ModulatedControlParameter:
    """
    A control parameter in the Nymphes synthesizer that can be modulated with the modulation matrix.
    For each of these control parameters, there are the following properties:
    - Value
    - LFO2 Modulation Amount
    - Mod Wheel Modulation Amount
    - Velocity Modulation Amount
    - Aftertouch Modulation Amount

    All properties are MIDI-controlled on the Nymphes, so they have a range of 0 to 127
    """

    def __init__(self, dispatcher, osc_send_function, midi_send_function, base_osc_address, value_cc, lfo2_cc, wheel_cc, velocity_cc,
                 aftertouch_cc):
        """
        dispatcher is an OSC dispatcher that we use to map incoming OSC messages with our OSC addresses.
        osc_client is used for sending outgoing OSC messages
        base_osc_address is a string.
        midi_out_port is a mido MIDI output port used when sending MIDI messages
        lfo2_cc, wheel_cc, velocity_cc and aftertouch_cc are the MIDI CC numbers used for each modulation type.
        """
        self._base_osc_address = base_osc_address
        self._value = 0

        # Store the MIDI CC numbers
        self._value_cc = value_cc
        self._lfo2_cc = lfo2_cc
        self._wheel_cc = wheel_cc
        self._velocity_cc = velocity_cc
        self._aftertouch_cc = aftertouch_cc

        # Create the modulation amounts object
        self.mod = self.ModulationAmounts(dispatcher, osc_send_function, midi_send_function, self._base_osc_address, self._lfo2_cc, self._wheel_cc, self._velocity_cc, self._aftertouch_cc)

        # Map OSC messages
        dispatcher.map(self._base_osc_address + '/value', self.on_osc_value_message)

        # Store the OSC client for when we need to send out OSC messages
        self._osc_send_function = osc_send_function

        # Store MIDI out port for when we need to send out MIDI messages
        self._midi_send_function = midi_send_function

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

            # Send out an OSC message with the new value
            self._osc_send_function.send_message(self._base_osc_address + '/value', self._value)

        except ValueError:
            raise ValueError(f'value could not be converted to an int: {val}') from None

    def on_osc_value_message(self, address, *args):
        # Get the new value and store it
        val = args[0]
        self.value = val
        print(f'{address}: {val}')

        # Send out a MIDI message
        if not self._midi_out_port.closed:
            msg = None
            self._midi_out_port.send(msg)

    class ModulationAmounts:
        def __init__(self, dispatcher, osc_send_function, midi_send_function, base_osc_address, lfo2_cc, wheel_cc, velocity_cc, aftertouch_cc):

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
            self._lfo2_cc = lfo2_cc
            self._wheel_cc = wheel_cc
            self._velocity_cc = velocity_cc
            self._aftertouch_cc = aftertouch_cc

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

        def on_osc_lfo2_message(self, address, *args):
            val = args[0]
            self._lfo2_value = val
            print(f'{address}: {val}')

            # Send a MIDI message to the Nymphes
            self._midi_send_function(midi_cc=self._lfo2_cc, value=self._lfo2_value)

        def on_osc_wheel_message(self, address, *args):
            val = args[0]
            self._wheel_value = val
            print(f'{address}: {val}')

            # Send a MIDI message to the Nymphes
            self._midi_send_function(midi_cc=self._wheel_cc, value=self._wheel_value)

        def on_osc_velocity_message(self, address, *args):
            val = args[0]
            self._velocity_value = val
            print(f'{address}: {val}')

            # Send a MIDI message to the Nymphes
            self._midi_send_function(midi_cc=self._velocity_cc, value=self._velocity_value)

        def on_osc_aftertouch_message(self, address, *args):
            val = args[0]
            self._aftertouch_value = val
            print(f'{address}: {val}')

            # Send a MIDI message to the Nymphes
            self._midi_send_function(midi_cc=self._aftertouch_cc, value=self._aftertouch_value)
