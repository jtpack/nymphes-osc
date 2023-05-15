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
        self._amp_params = NymphesOscAmpParams(self.dispatcher)
        self._mix_params = NymphesOscMixParams(self.dispatcher)
        self._lpf_params = NymphesOscLpfParams(self.dispatcher)
        self._hpf_params = NymphesOscHpfParams(self.dispatcher)
        self._pitch_filter_env_params = NymphesOscPitchFilterEnvParams(self.dispatcher)
        self._pitch_filter_lfo_params = NymphesOscPitchFilterLfoParams(self.dispatcher)
        self._lfo2_params = NymphesOscLfo2Params(self.dispatcher)

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
    
    @property
    def amp(self):
        return self._amp_params
    
    @property
    def mix(self):
        return self._mix_params
    
    @property
    def lpf(self):
        return self._lpf_params
    
    @property
    def hpf(self):
        return self._hpf_params

    @property
    def pitch_filter_env(self):
        return self._pitch_filter_env_params
    
    @property
    def pitch_filter_lfo(self):
        return self._pitch_filter_lfo_params
    
    @property
    def lfo2(self):
        return self._lfo2_params
    

# Classes for specific sections of the Nymphes Synthesizer
#

class NymphesOscOscillatorParams:
    """A class for tracking all of the control parameters for the oscillator"""

    def __init__(self, dispatcher):
        self._wave = NymphesOscModulatedControlParameter(dispatcher, '/osc/wave')
        self._level = NymphesOscModulatedControlParameter(dispatcher,'/osc/level')

    @property
    def wave(self):
        return self._wave
    
    @property
    def level(self):
        return self._level


class NymphesOscPitchParams:
    """A class for tracking all of pitch-related control parameters"""

    def __init__(self, dispatcher):
        self._detune = NymphesOscModulatedControlParameter(dispatcher, '/pitch/detune')
        self._chord = NymphesOscModulatedControlParameter(dispatcher, '/pitch/chord')
        self._env_depth = NymphesOscModulatedControlParameter(dispatcher, '/pitch/env_depth')
        self._lfo1 = NymphesOscModulatedControlParameter(dispatcher, '/pitch/lfo1')
        self._glide = NymphesOscModulatedControlParameter(dispatcher, '/pitch/glide')

    @property
    def detune(self):
        return self._detune

    @property
    def chord(self):
        return self._chord

    @property
    def env_depth(self):
        return self._env_depth

    @property
    def lfo1(self):
        return self._lfo1
    
    @property
    def glide(self):
        return self._glide


class NymphesOscAmpParams:
    """A class for tracking all of amplitude-related control parameters"""

    def __init__(self, dispatcher):
        self._attack = NymphesOscModulatedControlParameter(dispatcher, '/amp/attack')
        self._decay = NymphesOscModulatedControlParameter(dispatcher, '/amp/decay')
        self._sustain = NymphesOscModulatedControlParameter(dispatcher, '/amp/sustain')
        self._release = NymphesOscModulatedControlParameter(dispatcher, '/amp/release')
        self._level = NymphesOscControlParameter(dispatcher, '/amp/level/value')

    @property
    def attack(self):
        return self._attack

    @property
    def decay(self):
        return self._decay

    @property
    def sustain(self):
        return self._sustain
    
    @property
    def release(self):
        return self._release
    
    @property
    def level(self):
        return self._level


class NymphesOscMixParams:
    """A class for tracking all of mix-related control parameters"""

    def __init__(self, dispatcher):
        self._osc = NymphesOscModulatedControlParameter(dispatcher, '/mix/osc')
        self._sub = NymphesOscModulatedControlParameter(dispatcher, '/mix/sub')
        self._noise = NymphesOscModulatedControlParameter(dispatcher, '/mix/noise')

    @property
    def osc(self):
        return self._osc

    @property
    def sub(self):
        return self._sub

    @property
    def noise(self):
        return self._noise


class NymphesOscLpfParams:
    """A class for tracking all of LPF-related control parameters"""

    def __init__(self, dispatcher):
        self._cutoff = NymphesOscModulatedControlParameter(dispatcher, '/lpf/cutoff')
        self._resonance = NymphesOscModulatedControlParameter(dispatcher, '/lpf/resonance')
        self._tracking = NymphesOscModulatedControlParameter(dispatcher, '/lpf/tracking')
        self._env_depth = NymphesOscModulatedControlParameter(dispatcher, '/lpf/env_depth')
        self._lfo1 = NymphesOscModulatedControlParameter(dispatcher, '/lpf/lfo1')

    @property
    def cutoff(self):
        return self._cutoff

    @property
    def resonance(self):
        return self._resonance

    @property
    def tracking(self):
        return self._tracking

    @property
    def env_depth(self):
        return self._env_depth

    @property
    def lfo1(self):
        return self._lfo1


class NymphesOscHpfParams:
    """A class for tracking all of HPF-related control parameters"""

    def __init__(self, dispatcher):
        self._cutoff = NymphesOscModulatedControlParameter(dispatcher, '/hpf/cutoff')

    @property
    def cutoff(self):
        return self._cutoff
    

class NymphesOscPitchFilterEnvParams:
    """A class for tracking all control parameters related to the pitch/filter envelope generator"""

    def __init__(self, dispatcher):
        self._attack = NymphesOscModulatedControlParameter(dispatcher, '/pitch_filter_env/attack')
        self._decay = NymphesOscModulatedControlParameter(dispatcher, '/pitch_filter_env/decay')
        self._sustain = NymphesOscModulatedControlParameter(dispatcher, '/pitch_filter_env/sustain')
        self._release = NymphesOscModulatedControlParameter(dispatcher, '/pitch_filter_env/release')

    @property
    def attack(self):
        return self._attack
    
    @property
    def decay(self):
        return self._decay

    @property
    def sustain(self):
        return self._sustain

    @property
    def release(self):
        return self._release


class NymphesOscPitchFilterLfoParams:
    """A class for tracking all control parameters related to the pitch/filter LFO (lfo1)"""

    def __init__(self, dispatcher):
        self._rate = NymphesOscModulatedControlParameter(dispatcher, '/lfo1/rate')
        self._wave = NymphesOscModulatedControlParameter(dispatcher, '/lfo1/wave')
        self._delay = NymphesOscModulatedControlParameter(dispatcher, '/lfo1/delay')
        self._fade = NymphesOscModulatedControlParameter(dispatcher, '/lfo1/fade')
        self._type = NymphesOscLfoTypeParameter(dispatcher, '/lfo1/type/value')
        self._key_sync = NymphesOscLfoKeySyncParameter(dispatcher, '/lfo1/key_sync/value')

    @property
    def rate(self):
        return self._rate
    
    @property
    def wave(self):
        return self._wave
    
    @property
    def delay(self):
        return self._delay

    @property
    def fade(self):
        return self._fade

    @property
    def type(self):
        return self._type

    @property
    def key_sync(self):
        return self._key_sync
    

class NymphesOscLfo2Params:
    """A class for tracking all control parameters related to LFO2"""

    def __init__(self, dispatcher):
        self._rate = NymphesOscModulatedControlParameter(dispatcher, '/lfo2/rate')
        self._wave = NymphesOscModulatedControlParameter(dispatcher, '/lfo2/wave')
        self._delay = NymphesOscModulatedControlParameter(dispatcher, '/lfo2/delay')
        self._fade = NymphesOscModulatedControlParameter(dispatcher, '/lfo2/fade')
        self._type = NymphesOscLfoTypeParameter(dispatcher, '/lfo2/type/value')
        self._key_sync = NymphesOscLfoKeySyncParameter(dispatcher, '/lfo2/key_sync/value')

    @property
    def rate(self):
        return self._rate
    
    @property
    def wave(self):
        return self._wave
    
    @property
    def delay(self):
        return self._delay

    @property
    def fade(self):
        return self._fade

    @property
    def type(self):
        return self._type

    @property
    def key_sync(self):
        return self._key_sync
    
        
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
