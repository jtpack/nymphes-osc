from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido

class NymphesOscController:
    """
    A class used for OSC control of all of the control parameters of the Dreadbox Nymphes synthesizer.
    We communicate with a Pure Data patch via OSC. The patch communicates with the Nymphes via MIDI.    
    """

    def __init__(self, incoming_host, incoming_port, outgoing_host, outgoing_port, nymphes_midi_channel):
        # Prepare OSC objects
        #

        self.incoming_host = incoming_host
        self.incoming_port = incoming_port
        self.outgoing_host = outgoing_host
        self.outgoing_port = outgoing_port

        # The OSC Server, which receives incoming OSC messages on a background thread
        #

        self.osc_server = None
        self.osc_server_thread = None

        self.dispatcher = Dispatcher()

        # The OSC Client, which sends outgoing OSC messages
        self.osc_client = SimpleUDPClient(outgoing_host, outgoing_port)

        # The MIDI channel for the connected Nymphes synthesizer
        self.nymphes_midi_channel = nymphes_midi_channel

        # MIDI IO port for messages to and from Nymphes
        self.nymphes_midi_port = None
        
        # Create the control parameter objects
        self._oscillator_params = NymphesOscOscillatorParams(self.dispatcher, self.osc_client)
        self._pitch_params = NymphesOscPitchParams(self.dispatcher, self.osc_client)
        self._amp_params = NymphesOscAmpParams(self.dispatcher, self.osc_client)
        self._mix_params = NymphesOscMixParams(self.dispatcher, self.osc_client)
        self._lpf_params = NymphesOscLpfParams(self.dispatcher, self.osc_client)
        self._hpf_params = NymphesOscHpfParams(self.dispatcher, self.osc_client)
        self._pitch_filter_env_params = NymphesOscPitchFilterEnvParams(self.dispatcher, self.osc_client)
        self._pitch_filter_lfo_params = NymphesOscPitchFilterLfoParams(self.dispatcher, self.osc_client)
        self._lfo2_params = NymphesOscLfo2Params(self.dispatcher, self.osc_client)
        self._reverb_params = NymphesOscReverbParams(self.dispatcher, self.osc_client)
        self._play_mode_parameter = NymphesOscPlayModeParameter(self.dispatcher, self.osc_client)
        self._mod_source_parameter = NymphesOscModSourceParameter(self.dispatcher, self.osc_client)
        self._legato_parameter = NymphesOscLegatoParameter(self.dispatcher, self.osc_client)

    def start_osc_server(self):
        self.osc_server = BlockingOSCUDPServer((self.incoming_host, self.incoming_port), self.dispatcher)
        self.osc_server_thread = threading.Thread(target=self.osc_server.serve_forever)
        self.osc_server_thread.start()

    def stop_osc_server(self):
        if self.osc_server is not None:
            self.osc_server.shutdown()
            self.osc_server.server_close()
            self.osc_server = None
            self.osc_server_thread.join()
            self.osc_server_thread = None

    def open_nymphes_midi_port(self):
        """
        Opens MIDI IO port for Nymphes synthesizer
        """
        port_name = 'Nymphes Bootloader'
        self.nymphes_midi_port = mido.open_ioport(port_name)

    def close_nymphes_midi_port(self):
        """
        Closes the MIDI IO port for the Nymphes synthesizer
        """
        if self.nymphes_midi_port is not None:
            self.nymphes_midi_port.close()

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
    
    @property
    def reverb(self):
        return self._reverb_params
    
    @property
    def play_mode(self):
        return self._play_mode_parameter
    
    @property
    def mod_source(self):
        return self._mod_source_parameter
    
    @property
    def legato(self):
        return self._legato_parameter
    

# Classes for specific sections of the Nymphes Synthesizer
#

class NymphesOscOscillatorParams:
    """A class for tracking all of the control parameters for the oscillator"""

    def __init__(self, dispatcher, osc_client, midi_output_port):
        self._wave = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/osc/wave')
        self._pulsewidth = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/osc/pulsewidth')

    @property
    def wave(self):
        return self._wave
    
    @property
    def pulsewidth(self):
        return self._pulsewidth


class NymphesOscPitchParams:
    """A class for tracking all of pitch-related control parameters"""

    def __init__(self, dispatcher, osc_client):
        self._detune = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/pitch/detune')
        self._chord = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/pitch/chord')
        self._env_depth = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/pitch/env_depth')
        self._lfo1 = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/pitch/lfo1')
        self._glide = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/pitch/glide')

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

    def __init__(self, dispatcher, osc_client):
        self._attack = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/amp/attack')
        self._decay = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/amp/decay')
        self._sustain = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/amp/sustain')
        self._release = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/amp/release')
        self._level = NymphesOscControlParameter(dispatcher, osc_client, '/amp/level/value', min_val=0, max_val=127)

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

    def __init__(self, dispatcher, osc_client):
        self._osc = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/mix/osc')
        self._sub = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/mix/sub')
        self._noise = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/mix/noise')

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

    def __init__(self, dispatcher, osc_client):
        self._cutoff = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lpf/cutoff')
        self._resonance = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lpf/resonance')
        self._tracking = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lpf/tracking')
        self._env_depth = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lpf/env_depth')
        self._lfo1 = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lpf/lfo1')

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

    def __init__(self, dispatcher, osc_client):
        self._cutoff = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/hpf/cutoff')

    @property
    def cutoff(self):
        return self._cutoff
    

class NymphesOscPitchFilterEnvParams:
    """A class for tracking all control parameters related to the pitch/filter envelope generator"""

    def __init__(self, dispatcher, osc_client):
        self._attack = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/pitch_filter_env/attack')
        self._decay = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/pitch_filter_env/decay')
        self._sustain = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/pitch_filter_env/sustain')
        self._release = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/pitch_filter_env/release')

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

    def __init__(self, dispatcher, osc_client):
        self._rate = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lfo1/rate')
        self._wave = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lfo1/wave')
        self._delay = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lfo1/delay')
        self._fade = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lfo1/fade')
        self._type = NymphesOscLfoTypeParameter(dispatcher, osc_client, '/lfo1/type/value')
        self._key_sync = NymphesOscLfoKeySyncParameter(dispatcher, osc_client, '/lfo1/key_sync/value')

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

    def __init__(self, dispatcher, osc_client):
        self._rate = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lfo2/rate')
        self._wave = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lfo2/wave')
        self._delay = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lfo2/delay')
        self._fade = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/lfo2/fade')
        self._type = NymphesOscLfoTypeParameter(dispatcher, osc_client, '/lfo2/type/value')
        self._key_sync = NymphesOscLfoKeySyncParameter(dispatcher, osc_client, '/lfo2/key_sync/value')

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
    
class NymphesOscReverbParams:
    """A class for tracking all control parameters related to reverb"""

    def __init__(self, dispatcher, osc_client):
        self._size = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/reverb/size')
        self._decay = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/reverb/decay')
        self._filter = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/reverb/filter')
        self._mix = NymphesOscModulatedControlParameter(dispatcher, osc_client, '/reverb/mix')

    @property
    def size(self):
        return self._size
    
    @property
    def decay(self):
        return self._decay

    @property
    def filter(self):
        return self._filter

    @property
    def mix(self):
        return self._mix
        
class NymphesOscControlParameter:
    """
    A control parameter in the Nymphes synthesizer that cannot be modulated by the modulation matrix.
    It has only one property: value.
    Its range is 0 to 127.
    """

    def __init__(self, dispatcher, osc_client, osc_address, min_val, max_val, midi_cc, osc_callback=None):
        """
        dispatcher is an OSC dispatcher object.
        osc_client is an OSC client object that we use for sending OSC messages.
        osc_address is a string.
        midi_out_port is a mido midi output port.
        """

        self._value = 0
        self.min_val = min_val
        self.max_val = max_val
        
        self._osc_address = osc_address

        # Register for OSC messages at our OSC address
        dispatcher.map(self._osc_address, self.on_osc_message)

        # Store the OSC client for when we need to send out OSC messages
        self._osc_client = osc_client

        # Callback that we call when an incoming OSC message change the value.
        # It will be called on a background thread, so the receiver needs to be sure
        # to prevent any thread handling issues.
        # The callback will be called with one argument: the new value of the parameter.
        self._osc_callback = osc_callback

        # Store the MIDI CC number for this parameter
        self._midi_cc = midi_cc

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        try:
            # Convert value to an integer
            new_val = int(val)

            # Validate the value
            if new_val < self.min_val or new_val > self.max_val:
                raise Exception(f'Value {new_val} must be within {self.min_val} and {self.max_val}')

            # Store the new value
            self._value = new_val

            # Send out an OSC message with the new value
            self._osc_client.send_message(self._osc_address, self._value)

        except ValueError:
            raise ValueError(f'value could not be converted to an int: {val}') from None

    def on_osc_message(self, address, *args):
        # Get the new value
        val = args[0]

        # Set _value, our private variable, rather than using the setter,
        # as we don't want to trigger an outgoing OSC message
        self._value = val

        print(f'{address}: {val}')

        # Call the callback if it has been set
        if self._osc_callback is not None:
            self._osc_callback(self.value)


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
        def __init__(self, dispatcher, osc_client, base_osc_address, midi_out_port, lfo2_cc, wheel_cc, velocity_cc, aftertouch_cc):
            self.base_osc_address = base_osc_address
            self._lfo2 = 0
            self._wheel = 0
            self._velocity = 0
            self._aftertouch = 0

            # Map OSC messages
            dispatcher.map(self.base_osc_address + '/mod/lfo2', self.on_osc_lfo2_message)
            dispatcher.map(self.base_osc_address + '/mod/wheel', self.on_osc_wheel_message)
            dispatcher.map(self.base_osc_address + '/mod/velocity', self.on_osc_velocity_message)
            dispatcher.map(self.base_osc_address + '/mod/aftertouch', self.on_osc_aftertouch_message)

            # Store the OSC client for when we need to send out OSC messages
            self._osc_client = osc_client

            # Store MIDI out port for when we need to send out MIDI messages
            self._midi_out_port = midi_out_port

            # Store the MIDI CC numbers for each modulation type
            self._lfo2_cc = lfo2_cc
            self._wheel_cc = wheel_cc
            self._velocity_cc = velocity_cc
            self._aftertouch_cc = aftertouch_cc
        
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

                # Send out an OSC message with the new value
                self._osc_client.send_message(self.base_osc_address + '/mod/lfo2', self._lfo2)
                
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

                # Send out an OSC message with the new value
                self._osc_client.send_message(self.base_osc_address + '/mod/wheel', self._wheel)
                
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

                # Send out an OSC message with the new value
                self._osc_client.send_message(self.base_osc_address + '/mod/velocity', self._velocity)
                
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

                # Send out an OSC message with the new value
                self._osc_client.send_message(self.base_osc_address + '/mod/aftertouch', self._aftertouch)
                
            except ValueError:
                raise ValueError(f'value could not be converted to an int: {value}') from None
            
        def on_osc_lfo2_message(self, address, *args):
            val = args[0]
            self._lfo2 = val
            print(f'{address}: {val}')

            # Call the callback if it has been set
            if self._lfo2_osc_callback is not None:
                self._lfo2_osc_callback(self.lfo2)

        def on_osc_wheel_message(self, address, *args):
            val = args[0]
            self._wheel = val
            print(f'{address}: {val}')

            # Call the callback if it has been set
            if self._wheel_osc_callback is not None:
                self._wheel_osc_callback(self.wheel)

        def on_osc_velocity_message(self, address, *args):
            val = args[0]
            self._velocity = val
            print(f'{address}: {val}')

            # Call the callback if it has been set
            if self._velocity_osc_callback is not None:
                self._velocity_osc_callback(self.velocity)

        def on_osc_aftertouch_message(self, address, *args):
            val = args[0]
            self._aftertouch = val
            print(f'{address}: {val}')

            # Call the callback if it has been set
            if self._aftertouch_osc_callback is not None:
                self._aftertouch_osc_callback(self.aftertouch)

        
    def __init__(self, dispatcher, osc_client, base_osc_address, midi_out_port, lfo2_cc, wheel_cc, velocity_cc, aftertouch_cc):
        """
        dispatcher is an OSC dispatcher that we use to map incoming OSC messages with our OSC addresses.
        osc_client is used for sending outgoing OSC messages
        base_osc_address is a string.
        midi_out_port is a mido MIDI output port used when sending MIDI messages
        lfo2_cc, wheel_cc, velocity_cc and aftertouch_cc are the MIDI CC numbers used for each modulation type.
        """
        self.base_osc_address = base_osc_address
        self._value = 0
        self.mod = self.ModulationAmounts(dispatcher, osc_client, base_osc_address, midi_out_port, value_cc)

        # Map OSC messages
        dispatcher.map(self.base_osc_address + '/value', self.on_osc_value_message)

        # Store the OSC client for when we need to send out OSC messages
        self._osc_client = osc_client

        # Store MIDI out port for when we need to send out MIDI messages
        self._midi_out_port = midi_out_port

        # Store the MIDI CC numbers for each modulation type
        self._lfo2_cc = lfo2_cc
        self._wheel_cc = wheel_cc
        self._velocity_cc = velocity_cc
        self._aftertouch_cc = aftertouch_cc

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
            self._osc_client.send_message(self.base_osc_address + '/value', self._value)
            
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




class NymphesOscLfoTypeParameter(NymphesOscControlParameter):
    """
    Control parameter for LFO type, which has four possible settings. These can be set using either their int values or string names.
    0 = 'bpm'
    1 = 'low'
    2 = 'high'
    3 = 'track'
    """

    def __init__(self, dispatcher, osc_client, osc_address):
        super().__init__(dispatcher, osc_client, osc_address, min_val=0, max_val=3)
        
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


class NymphesOscPlayModeParameter(NymphesOscControlParameter):
    """
    Control parameter for Play Mode, which has six possible values. These can be set using either their int values or string names.
    0 = 'polyphonic'
    1 = 'unison-6'
    2 = 'unison-4'
    3 = 'triphonic'
    4 = 'duophonic'
    5 - 'monophonic'
    """

    def __init__(self, dispatcher, osc_client):
        super().__init__(dispatcher, osc_client, osc_address='/play_mode', min_val=0, max_val=5)

    @property
    def string_value(self):
        if self.value == 0:
            return 'polyphonic'
        elif self.value == 1:
            return 'unison-6'
        elif self.value == 2:
            return 'unison-4'
        elif self.value == 3:
            return 'triphonic'
        elif self.value == 4:
            return 'duophonic'
        elif self.value == 5:
            return 'monophonic'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self.value}')
        
    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'polyphonic':
            self.value = 0
        elif string_val == 'unison-6':
            self.value = 1
        elif string_val == 'unison-4':
            self.value = 2
        elif string_val == 'triphonic':
            self.value = 3
        elif string_val == 'duophonic':
            self.value = 2
        elif string_val == 'monophonic':
            self.value = 1
        else:
            raise Exception(f'Invalid string_value: {string_val}')
        

class NymphesOscLfoKeySyncParameter(NymphesOscControlParameter):
    """
    Control parameter for LFO key sync, which has two possible settings. These can be set using either their int values or string names.
    0 = 'off'
    1 = 'on'
    """

    def __init__(self, dispatcher, osc_client, osc_address):
        super().__init__(dispatcher, osc_client, osc_address, min_val=0, max_val=1)
        
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


class NymphesOscLegatoParameter(NymphesOscControlParameter):
    """
    Control parameter for Legato, which has two possible settings. These can be set using their int values, string names, or True and False.
    0 = 'off'
    1 = 'on'
    """

    def __init__(self, dispatcher, osc_client):
        super().__init__(dispatcher, osc_client, osc_address='/legato', min_val=0, max_val=1)
        
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


class NymphesOscModSourceParameter(NymphesOscControlParameter):
    """
    Control parameter for Mod Source Selector, which has four possible settings. These can be set using either their int values or string names.
    0 = 'lfo2'
    1 = 'wheel'
    2 = 'velocity'
    3 = 'aftertouch'
    """

    def __init__(self, dispatcher, osc_client):
        super().__init__(dispatcher, osc_client, osc_address='/mod_source', min_val=0, max_val=3)
        
    @property
    def string_value(self):
        if self.value == 0:
            return 'lfo2'
        elif self.value == 1:
            return 'wheel'
        elif self.value == 2:
            return 'velocity'
        elif self.value == 3:
            return 'aftertouch'
        else:
            # It should not be possible to get here unless _value was directly manipulated.
            raise Exception(f'_value has an invalid value: {self.value}')
        
    @string_value.setter
    def string_value(self, string_val):
        if string_val == 'lfo2':
            self.value = 0
        elif string_val == 'wheel':
            self.value = 1
        elif string_val == 'velocity':
            self.value = 2
        elif string_val == 'aftertouch':
            self.value = 3
        else:
            raise Exception(f'Invalid string_value: {string_val}')
