from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading

class NymphesOscController:
    """
    A class used for OSC control of all of the control parameters of the Dreadbox Nymphes synthesizer.
    We communicate with a Pure Data patch via OSC. The patch communicates with the Nymphes via MIDI.    
    """

    def __init__(self, incoming_host, incoming_port, outgoing_host, outgoing_port):
        # Prepare OSC objects
        self.incoming_host = incoming_host
        self.incoming_port = incoming_port
        self.outgoing_host = outgoing_host
        self.outgoing_port = outgoing_port

        self.server = None
        self.server_thread = None

        self.dispatcher = Dispatcher()
        
        # Create the control parameter objects
        self._oscillator_params = NymphesOscOscillatorParams(self.dispatcher)
        self._pitch_params = NymphesOscPitchParams(self.dispatcher)

        # Start the OSC server in another thread

    def start_server(self):
        self.server = BlockingOSCUDPServer((self.incoming_host, self.incoming_port), self.dispatcher)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()        

    def stop_server(self):
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
            self.server_thread.join()
            self.server_thread = None

    @property
    def oscillator(self):
        return self._oscillator_params
    
    @property
    def pitch(self):
        return self._pitch_params
    




class NymphesOscOscillatorParams:
    """A class for tracking all of the control parameters for the oscillator"""

    def __init__(self, dispatcher):
        self._wave = NymphesOscModulatedControlParameter(dispatcher, '/osc/wave')
        self._pulsewidth = NymphesOscModulatedControlParameter(dispatcher,'/osc/pulsewidth')

    @property
    def wave(self):
        return self._wave
    
    @property
    def pulsewidth(self):
        return self._pulsewidth


class NymphesOscPitchParams:
    """A class for tracking all of pitch-related control parameters"""

    def __init__(self, dispatcher):
        self._detune = NymphesOscModulatedControlParameter(dispatcher, '/pitch/detune')
        self._chord = NymphesOscModulatedControlParameter(dispatcher, '/pitch/chord')
        self._env_depth = NymphesOscModulatedControlParameter(dispatcher, '/pitch/env_depth')
        self._lfo1 = NymphesOscModulatedControlParameter(dispatcher, '/pitch/lfo1')
        self._glide = NymphesOscModulatedControlParameter(dispatcher, '/pitch/glide')

        
class NymphesOscControlParameter:
    """
    A control parameter in the Nymphes synthesizer that cannot be modulated by the modulation matrix.
    It has only one property: value.
    Its range is 0 to 127.
    """

    def __init__(self, dispatcher, osc_address):
        """
        dispatcher is an OSC dispatcher object.
        osc_address is a string.
        """
        self._value = 0
        
        self._osc_address = osc_address

        # Register for OSC messages at our OSC address
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
            if new_val < 0 or new_val > 127:
                raise Exception(f'Invalid value: {new_val}')

            # Store the new value
            self._value = new_val
            
        except ValueError:
            raise ValueError(f'value could not be converted to an int: {val}') from None

    def on_osc_message(self, address, *args):
        val = args[0]
        self.value = val
        print(f'{address}: {val}')


class NymphesOscModulatedControlParameter:
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

    class ModulationAmounts:
        def __init__(self):
            self._lfo2 = 0
            self._wheel = 0
            self._velocity = 0
            self._aftertouch = 0
        
        @property
        def lfo2(self):
            return self._lfo2
        
        @lfo2.setter
        def lfo2(self, value):
            try:
                # Convert value to an integer
                new_val = int(value)

                # Validate the value
                if new_val < 0 or new_val > 127:
                    raise Exception(f'Invalid value: {new_val}')

                # Store the new value
                self._lfo2 = new_val
                
            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None
            
        @property
        def wheel(self):
            return self._wheel
        
        @wheel.setter
        def wheel(self, value):
            try:
                # Convert value to an integer
                new_val = int(value)

                # Validate the value
                if new_val < 0 or new_val > 127:
                    raise Exception(f'Invalid value: {new_val}')

                # Store the new value
                self._wheel = new_val
                
            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None
        
        @property
        def velocity(self):
            return self._velocity
        
        @velocity.setter
        def velocity(self, value):
            try:
                # Convert value to an integer
                new_val = int(value)

                # Validate the value
                if new_val < 0 or new_val > 127:
                    raise Exception(f'Invalid value: {new_val}')

                # Store the new value
                self._velocity = new_val
                
            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None
            
        @property
        def aftertouch(self):
            return self._aftertouch
        
        @aftertouch.setter
        def aftertouch(self, value):
            try:
                # Convert value to an integer
                new_val = int(value)

                # Validate the value
                if new_val < 0 or new_val > 127:
                    raise Exception(f'Invalid value: {new_val}')

                # Store the new value
                self._aftertouch = new_val
                
            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None

        
    def __init__(self, dispatcher, base_osc_address):
        """
        dispatcher is an OSC dispatcher that we use to map incoming OSC messages with our OSC addresses.
        base_osc_address is a string.
        """
        self.base_osc_address = base_osc_address
        self._value = 0
        self.modulation = self.ModulationAmounts()

        # Map OSC messages
        dispatcher.map(self.base_osc_address + '/value', self.on_osc_value_message)
        dispatcher.map(self.base_osc_address + '/mod/lfo2', self.on_osc_lfo2_message)
        dispatcher.map(self.base_osc_address + '/mod/wheel', self.on_osc_wheel_message)
        dispatcher.map(self.base_osc_address + '/mod/velocity', self.on_osc_velocity_message)
        dispatcher.map(self.base_osc_address + '/mod/aftertouch', self.on_osc_aftertouch_message)

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

    def on_osc_value_message(self, address, *args):
        val = args[0]
        self.value = val
        print(f'{address}: {val}')

    def on_osc_lfo2_message(self, address, *args):
        val = args[0]
        self.modulation.lfo2 = val
        print(f'{address}: {val}')

    def on_osc_wheel_message(self, address, *args):
        val = args[0]
        self.modulation.wheel = val
        print(f'{address}: {val}')

    def on_osc_velocity_message(self, address, *args):
        val = args[0]
        self.modulation.velocity = val
        print(f'{address}: {val}')

    def on_osc_aftertouch_message(self, address, *args):
        val = args[0]
        self.modulation.aftertouch = val
        print(f'{address}: {val}')

class NymphesOscLfoTypeParameter:
    """
    Control parameter for LFO type, which has four possible settings. These can be set using either their int values or string names.
    0 = 'bpm'
    1 = 'low'
    2 = 'high'
    3 = 'track'
    """

    def __init__(self):
        self._value = 0

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        try:
            # Convert value to an integer
            new_val = int(val)

            # Validate the value
            if new_val < 0 or new_val > 3:
                raise Exception(f'Invalid value: {new_val}')

            # Store the new value
            self._value = new_val
            
        except ValueError:
            raise ValueError(f'value could not be converted to an int: {val}') from None
        
    @property
    def string_value(self):
        if self._value == 0:
            return 'bpm'
        elif self._value == 1:
            return 'low'
        elif self._value == 2:
            return 'high'
        elif self._value == 3:
            return 'track'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self._value}')
        
    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'bpm':
            self._value = 0
        elif string_val == 'low':
            self._value = 1
        elif string_val == 'high':
            self._value = 2
        elif string_val == 'track':
            self._value = 3
        else:
            raise Exception(f'Invalid string_value: {string_val}')


class NymphesOscPlayModeParameter:
    """
    Control parameter for Play Mode, which has six possible values. These can be set using either their int values or string names.
    0 = 'polyphonic'
    1 = 'unison-6'
    2 = 'unison-4'
    3 = 'triphonic'
    4 = 'duophonic'
    5 - 'monophonic'
    """

    def __init__(self):
        self._value = 0

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        try:
            # Convert value to an integer
            new_val = int(val)

            # Validate the value
            if new_val < 0 or new_val > 5:
                raise Exception(f'Invalid value: {new_val}')

            # Store the new value
            self._value = new_val
            
        except ValueError:
            raise ValueError(f'value could not be converted to an int: {val}') from None
        
    @property
    def string_value(self):
        if self._value == 0:
            return 'polyphonic'
        elif self._value == 1:
            return 'unison-6'
        elif self._value == 2:
            return 'unison-4'
        elif self._value == 3:
            return 'triphonic'
        elif self._value == 4:
            return 'duophonic'
        elif self._value == 5:
            return 'monophonic'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self._value}')
        
    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'polyphonic':
            self._value = 0
        elif string_val == 'unison-6':
            self._value = 1
        elif string_val == 'unison-4':
            self._value = 2
        elif string_val == 'triphonic':
            self._value = 3
        elif string_val == 'duophonic':
            self._value = 2
        elif string_val == 'monophonic':
            self._value = 1
        else:
            raise Exception(f'Invalid string_value: {string_val}')
        

class NymphesOscLfoKeySyncParameter:
    """
    Control parameter for LFO key sync, which has two possible settings. These can be set using either their int values or string names.
    0 = 'off'
    1 = 'on'
    """

    def __init__(self):
        self._value = 0

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        try:
            # Convert value to an integer
            new_val = int(val)

            # Validate the value
            if new_val < 0 or new_val > 1:
                raise Exception(f'Invalid value: {new_val}')

            # Store the new value
            self._value = new_val
            
        except ValueError:
            raise ValueError(f'value could not be converted to an int: {val}') from None
        
    @property
    def string_value(self):
        if self._value == 0:
            return 'off'
        elif self._value == 1:
            return 'on'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self._value}')
        
    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'off':
            self._value = 0
        elif string_val == 'on':
            self._value = 1
        else:
            raise Exception(f'Invalid string_value: {string_val}')

class NymphesOscLegatoParameter:
    """
    Control parameter for Legato, which has two possible settings. These can be set using their int values, string names, or True and False.
    0 = 'off'
    1 = 'on'
    """

    def __init__(self):
        self._value = 0

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        try:
            # Convert value to an integer
            new_val = int(val)

            # Validate the value
            if new_val < 0 or new_val > 1:
                raise Exception(f'Invalid value: {new_val}')

            # Store the new value
            self._value = new_val
            
        except ValueError:
            raise ValueError(f'value could not be converted to an int: {val}') from None
        
    @property
    def string_value(self):
        if self._value == 0:
            return 'off'
        elif self._value == 1:
            return 'on'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self._value}')
        
    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'off':
            self._value = 0
        elif string_val == 'on':
            self._value = 1
        else:
            raise Exception(f'Invalid string_value: {string_val}')


class NymphesOscModSourceParameter:
    """
    Control parameter for Mod Source Selector, which has four possible settings. These can be set using either their int values or string names.
    0 = 'lfo2'
    1 = 'wheel'
    2 = 'velocity'
    3 = 'aftertouch'
    """

    def __init__(self):
        self._value = 0

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        try:
            # Convert value to an integer
            new_val = int(val)

            # Validate the value
            if new_val < 0 or new_val > 3:
                raise Exception(f'Invalid value: {new_val}')

            # Store the new value
            self._value = new_val
            
        except ValueError:
            raise ValueError(f'value could not be converted to an int: {val}') from None
        
    @property
    def string_value(self):
        if self._value == 0:
            return 'lfo2'
        elif self._value == 1:
            return 'wheel'
        elif self._value == 2:
            return 'velocity'
        elif self._value == 3:
            return 'aftertouch'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self._value}')
        
    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'lfo2':
            self._value = 0
        elif string_val == 'wheel':
            self._value = 1
        elif string_val == 'velocity':
            self._value = 2
        elif string_val == 'aftertouch':
            self._value = 3
        else:
            raise Exception(f'Invalid string_value: {string_val}')
