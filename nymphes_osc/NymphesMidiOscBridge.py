from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
import mido.backends.rtmidi
from rtmidi import InvalidPortError
import time
from .OscillatorParams import OscillatorParams
from .PitchParams import PitchParams
from .AmpParams import AmpParams
from .HpfParams import HpfParams
from .Lfo1Params import Lfo1Params
from .Lfo2Params import Lfo2Params
from .LpfParams import LpfParams
from .MixParams import MixParams
from .PitchFilterEnvParams import PitchFilterEnvParams
from .ReverbParams import ReverbParams
from .ControlParameter_PlayMode import ControlParameter_PlayMode
from .ControlParameter_ModSource import ControlParameter_ModSource
from .ControlParameter_Legato import ControlParameter_Legato
from nymphes_osc import sysex_handling
from pythonosc.osc_message_builder import OscMessageBuilder


class NymphesMidiOscBridge:
    """
    A class used for OSC control of all of the control parameters of the Dreadbox Nymphes synthesizer.
    We communicate with a Pure Data patch via OSC. The patch communicates with the Nymphes via MIDI.
    """

    def __init__(self, midi_channel, osc_in_host, osc_in_port, osc_out_host, osc_out_port):
        # Prepare OSC objects
        #
        self.midi_channel = midi_channel-1 # mido library is zero-referenced, so MIDI channel 1 is specified as 0
        self.in_host = osc_in_host
        self.in_port = osc_in_port
        self.out_host = osc_out_host
        self.out_port = osc_out_port

        # The OSC Server, which receives OSC messages on a background thread
        #
        self._osc_server = None
        self._osc_server_thread = None

        self._dispatcher = Dispatcher()

        # OSC hosts, which we send OSC messages to.
        # key: hostname or ip address as a string. value: an osc client for the host
        self._osc_hosts = {}

        # MIDI IO port for messages to and from Nymphes
        self._nymphes_midi_port = None

        # Flag indicating whether we are connected to a Nymphes synthesizer
        self.nymphes_connected = False

        # Current Nymphes MIDI program number
        self.nymphes_midi_program_num = None

        # Preset objects for the presets in the Nymphes' memory.
        # If a full sysex dump has been done then we will have an
        # entry for every preset. If not, then we'll only have
        # entries for the presets that have been recalled since
        # connecting to the Nymphes
        self.nymphes_presets = {i: None for i in range(0, 49)}

        # MIDI IO port for keyboard controller
        self._midi_controller_port = None

        # Flag indicating whether we are connected to a keyboard controller
        self.midi_controller_connected = False

        # Create the control parameter objects
        self._oscillator_params = OscillatorParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)
        self._pitch_params = PitchParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)
        self._amp_params = AmpParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)
        self._mix_params = MixParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)
        self._lpf_params = LpfParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)
        self._hpf_params = HpfParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)
        self._pitch_filter_env_params = PitchFilterEnvParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)
        self._lfo1_params = Lfo1Params(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)
        self._lfo2_params = Lfo2Params(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)
        self._reverb_params = ReverbParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)
        self._play_mode_parameter = ControlParameter_PlayMode(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)
        self._mod_source_parameter = ControlParameter_ModSource(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)
        self._legato_parameter = ControlParameter_Legato(self._dispatcher, self._osc_send_function, self._nymphes_midi_cc_send_function)

        # Register for OSC messages not associated with our control parameter objects
        self._dispatcher.map('/mod_source', self._on_mod_source_osc_message)
        self._dispatcher.map('/mod_wheel', self._on_mod_wheel_osc_message)
        self._dispatcher.map('/aftertouch', self._on_aftertouch_osc_message)
        self._dispatcher.map('/load_preset_file', self._on_load_preset_file_osc_message)
        self._dispatcher.map('/save_preset_file', self._on_load_preset_file_osc_message)
        self._dispatcher.map('/add_host', self._on_add_host_osc_message)
        self._dispatcher.map('/remove_host', self._on_remove_host_osc_message)
        #self._dispatcher.map('/connect_midi_controller', self._on_connect_midi_controller_osc_message)
        #self._dispatcher.map('/disconnect_midi_controller', self._on_disconnect_midi_controller_osc_message)

    def start_osc_server(self):
        self._osc_server = BlockingOSCUDPServer((self.in_host, self.in_port), self._dispatcher)
        self._osc_server_thread = threading.Thread(target=self._osc_server.serve_forever)
        self._osc_server_thread.start()
        
        self.send_status(f'Started OSC Server at {self.in_host}:{self.in_port}')
        # self.send_status(f'in_host: {self.in_host}')
        # self.send_status(f'in_port: {self.in_port}')
        # self.send_status(f'out_host: {self.out_host}')
        # self.send_status(f'out_port: {self.out_port}')

    def stop_osc_server(self):
        if self._osc_server is not None:
            self._osc_server.shutdown()
            self._osc_server.server_close()
            self._osc_server = None
            self._osc_server_thread.join()
            self._osc_server_thread = None
            self.send_status('Stopped OSC Server')

    def connect_nymphes_midi_port(self, port_name):
        """
        Opens MIDI IO port for Nymphes synthesizer
        """
        # Connect to the port
        self._nymphes_midi_port = mido.open_ioport(port_name)

        # Update connection flag
        self.nymphes_connected = True

        self.send_status(f'Connected to Nymphes (MIDI Port: {self._nymphes_midi_port.name})')
        #self.send_status(f'Using MIDI channel {self.midi_channel + 1}')

    def disconnect_nymphes_midi_port(self):
        """
        Closes the MIDI IO port for the Nymphes synthesizer
        """
        if self.nymphes_connected:
            # Close the port
            self._nymphes_midi_port.close()
            self.send_status(f'Closed MIDI Port {self._nymphes_midi_port.name}')

            # We no longer need this port
            self._nymphes_midi_port = None

            # Update connection flag
            self.nymphes_connected = False

        else:
            raise Exception('No Nymphes MIDI port is connected')

    def _get_connected_nymphes_midi_port_name(self):
        """
        Checks whether there is a Dreadbox Nymphes synthesizer connected.
        Returns the name of the midi port if it is connected.
        Returns None if no Nymphes is connected.
        """

        # Return the first port name that contains the word nymphes
        for port_name in mido.get_output_names():
            if 'nymphes' in (port_name).lower():
                return port_name
            
        # If we get here, then there was no matching port
        return None

    def _detect_nymphes_connection(self):
        """
        Check whether a nymphes synthesizer is connected.
        Open a midi port when a nymphes is connected, and close
        when it disconnects.
        """
        # Check whether the Nymphes is connected
        try:
            port_name = self._get_connected_nymphes_midi_port_name()
            
            if port_name is not None:
                # A nymphes is connected
                if not self.nymphes_connected:
                    # It has just been connected. Open the port.
                    self.connect_nymphes_midi_port(port_name)
            
            else:
                # A nymphes is not connected
                if self.nymphes_connected:
                    # It has just been disconnected. Close the port.
                    self.disconnect_nymphes_midi_port()
            
        except InvalidPortError:
            self.send_status('ignoring error while attempting to get port names (rtmidi.InvalidPortError)')
                    
            
    def update(self):
        """
        Should be called regularly.
        """
        # Check for Nymphes
        self._detect_nymphes_connection()

        # Handle any incoming MIDI messages waiting for us
        if self.nymphes_connected:
            for midi_message in self._nymphes_midi_port.iter_pending():
                self.on_midi_message(midi_message)        

    def on_midi_message(self, midi_message):
        """
        To be called by the nymphes midi port when new midi messages are received
        """
        # Handle MIDI Control Change Messages
        #
        if midi_message.is_cc() and midi_message.channel == self.midi_channel:
            # Handle mod source control message
            if midi_message.control == 30:
                self._on_mod_source_midi_message(midi_message.value)

            # Handle control parameter message
            else:
                if self.amp.on_midi_message(midi_message):
                    return
                if self.hpf.on_midi_message(midi_message):
                    return
                if self.lfo1.on_midi_message(midi_message):
                    return
                if self.lfo2.on_midi_message(midi_message):
                    return
                if self.lpf.on_midi_message(midi_message):
                    return
                if self.mix.on_midi_message(midi_message):
                    return
                if self.oscillator.on_midi_message(midi_message):
                    return
                if self.pitch_filter_env.on_midi_message(midi_message):
                    return
                if self.pitch.on_midi_message(midi_message):
                    return
                if self.reverb.on_midi_message(midi_message):
                    return
                if self.play_mode.on_midi_message(midi_message):
                    return
                if self.mod_source.on_midi_message(midi_message):
                    return
                if self.legato.on_midi_message(midi_message):
                    return

        elif midi_message.type == 'sysex':
            self._on_nymphes_sysex_message(midi_message)

        elif midi_message.type == 'program_change' and midi_message.channel == self.midi_channel:
            self._on_program_change_midi_message(midi_message.program)

        else:
            # Some other unhandled midi message was received
            self.send_status(f'Unhandled MIDI Message Received: {midi_message}')

    def _on_nymphes_sysex_message(self, midi_message):
        """
        A sysex message has been received from the Nymphes.
        Try to interpret it as a preset.
        """
        p, preset_import_type, user_or_factory, bank_number, preset_number = \
            sysex_handling.preset_from_sysex_data(midi_message.data)

        persistent_import = True if preset_import_type == 0x01 else False
        user_preset = True if user_or_factory == 0x00 else False

        # Calculate the index to use when storing this preset data

        status_message = 'Nymphes Preset Received:'
        if persistent_import:
            status_message += ' Persistent Import'
        else:
            status_message += ' Non-Persistent Import'

        status_message += f', Bank {bank_number}'

        if user_preset:
            status_message += f', User Preset {preset_number}'
        else:
            status_message += f', Factory Preset {preset_number}'

        self.send_status(status_message)


    def _nymphes_midi_cc_send_function(self, midi_cc, value):
        """
        A function used to send a MIDI CC message to the Nymphes synthesizer.
        Every member object in NymphesOscController is given a reference
        to this function so it can send MIDI CC messages.
        """
        if self.nymphes_connected:
            # Construct the MIDI message
            msg = mido.Message('control_change', channel=self.midi_channel, control=midi_cc, value=value)

            # Send the message
            self._nymphes_midi_port.send(msg)

    def _osc_send_function(self, osc_message):
        """
        A function used to send an OSC message.
        Every member object in NymphesOscController is given a reference
        to this function so it can send OSC messages.
        """
        for osc_client in self._osc_hosts.values():
            osc_client.send(osc_message)

    def _on_add_host_osc_message(self, address, *args):
        """
        A host has requested to be added
        """
        self.add_osc_host(host_name=str(args[0]), port=int(args[1]))

    def _on_remove_host_osc_message(self, address, *args):
        """
        A host has requested to be removed
        """
        self.remove_osc_host(host_name=args[0])

    def add_osc_host(self, host_name, port):
        """
        Add a new host to send OSC messages to.
        """
        # Validate host_name
        if not isinstance(host_name, str):
            raise Exception(f'host_name should be a string: {host_name}')

        # Validate port
        try:
            port_int = int(port)
        except ValueError:
            raise Exception(f'port could not be interpreted as an integer: {port}')

        # Check whether there's already an entry for this host
        if host_name in self._osc_hosts.keys():
            self.send_status(f'host already added ({host_name})')
            return

        # Create an osc client for this host
        client = SimpleUDPClient(host_name, port_int)

        # Store the client
        self._osc_hosts[host_name] = client

        # Send status update
        self.send_status(f'Added host: {host_name} on port {port_int}')

        # Send osc notification to the new host
        msg = OscMessageBuilder(address='/host_added')
        msg = msg.build()
        client.send(msg)

    def remove_osc_host(self, host_name):
        """
        Remove a host that was listening for OSC messages.
        """
        # Validate host_name
        if not isinstance(host_name, str):
            raise Exception(f'host_name should be a string: {host_name}')

        # Remove the host, if it was previously added
        if host_name in self._osc_hosts.keys():
            # Remove the host from the collection but get a reference to
            # it so we can send it one last message confirming that it has
            # been removed
            osc_client = self._osc_hosts.pop(host_name)

            # Send osc notification to the host that has been removed
            msg = OscMessageBuilder(address='/host_removed')
            msg = msg.build()
            osc_client.send(msg)

            # Status update
            self.send_status(f'Removed host: {host_name}')

    def _on_mod_source_osc_message(self, address, *args):
        """
        An OSC host has just sent a message to set the mod source
        0 = 'lfo2'
        1 = 'wheel'
        2 = 'velocity'
        3 = 'aftertouch'
        """

        mod_source = args[0]

        # Send the new mod source to all parameter groups.
        #
        self.amp.set_mod_source(mod_source)
        self.hpf.set_mod_source(mod_source)
        self.lfo1.set_mod_source(mod_source)
        self.lfo2.set_mod_source(mod_source)
        self.lpf.set_mod_source(mod_source)
        self.mix.set_mod_source(mod_source)
        self.oscillator.set_mod_source(mod_source)
        self.pitch_filter_env.set_mod_source(mod_source)
        self.pitch.set_mod_source(mod_source)
        self.reverb.set_mod_source(mod_source)

        # Send the new mod source to Nymphes
        #
        if self.nymphes_connected:
            # Construct the MIDI message
            msg = mido.Message('control_change',
                               channel=self.midi_channel,
                               control=30,
                               value=mod_source)

            # Send the message
            self._nymphes_midi_port.send(msg)

    def _on_mod_source_midi_message(self, mod_source):
        # Send the new mod source to all parameter groups.
        #
        self.amp.set_mod_source(mod_source)
        self.hpf.set_mod_source(mod_source)
        self.lfo1.set_mod_source(mod_source)
        self.lfo2.set_mod_source(mod_source)
        self.lpf.set_mod_source(mod_source)
        self.mix.set_mod_source(mod_source)
        self.oscillator.set_mod_source(mod_source)
        self.pitch_filter_env.set_mod_source(mod_source)
        self.pitch.set_mod_source(mod_source)
        self.reverb.set_mod_source(mod_source)

        # Send to OSC hosts
        msg = OscMessageBuilder(address='/mod_source')
        msg.add_arg(int(mod_source))
        msg = msg.build()
        self._osc_send_function(msg)

    def _on_mod_wheel_osc_message(self, address, *args):
        """
        An OSC host has just sent a message to send a MIDI Mod Wheel message.
        """
        value = args[0]

        if self.nymphes_connected:
            # Construct the MIDI message
            msg = mido.Message('control_change',
                               channel=self.midi_channel,
                               control=1,
                               value=value)

            # Send the message
            self._nymphes_midi_port.send(msg)

    def _on_aftertouch_osc_message(self, address, *args):
        """
        An OSC host has just sent a message to send a MIDI channel aftertouch message
        """
        value = args[0]

        if self.nymphes_connected:
            # Construct the MIDI message
            msg = mido.Message('aftertouch',
                               channel=self.midi_channel,
                               value=value)

            # Send the message
            self._nymphes_midi_port.send(msg)

    def _on_program_change_midi_message(self, program_num):
        """
        A MIDI program change message has just been received from the Nymphes,
        indicating that a preset has just been loaded.
        """
        self.nymphes_midi_program_num = program_num

        # Inform OSC hosts
        msg = OscMessageBuilder(address='/nymphes_program_changed')
        msg.add_arg(int(self.nymphes_midi_program_num))
        msg = msg.build()
        self._osc_send_function(msg)

        self.send_status(f'Program Change {program_num}')

    def _on_load_preset_file_osc_message(self, address, *args):
        """
        An OSC message has just been received to load a preset file
        """
        # Argument 0 is the filepath
        filepath = str(args[0])

        self.load_preset_file(filepath)
        
    def _on_save_preset_file_osc_message(self, address, *args):
        """
        An OSC message has just been received to save a preset file
        """
        # Argument 0 is the filepath
        filepath = str(args[0])

        self.save_preset_file(filepath)

    def load_preset_file(self, filepath):
        # The following is just a test
        #
        # Load the preset file into a preset object
        preset_object = sysex_handling.load_preset_file(filepath)

        # Send it via sysex to the Nymphes
        #
        # Create MIDI sysex data from it
        sysex_data = sysex_handling.sysex_data_from_preset_object(preset_object=preset_object,
                                                                  preset_import_type=0,
                                                                  user_or_factory=0,
                                                                  bank_number=5,
                                                                  preset_number=2)

        # Create a sysex message
        msg = mido.Message('sysex', data=sysex_data)

        if self.nymphes_connected:
            self._nymphes_midi_port.send(msg)
            self.send_status('Sent sysex message')

        # TODO: Update our OSC hosts

        # Status update
        self.send_status(f'loaded preset file: {filepath}')

        # Send out OSC notification
        msg = OscMessageBuilder(address='/loaded_preset_file')
        msg.add_arg(str(filepath))
        msg = msg.build()
        self._osc_send_function(msg)

    def save_preset_file(self, filepath):
        # TODO: Actually save the current preset

        # Status update
        self.send_status(f'saved preset file: {filepath}')

        # Send out OSC notification
        msg = OscMessageBuilder(address='/saved_preset_file')
        msg.add_arg(str(filepath))
        msg = msg.build()
        self._osc_send_function(msg)

    def send_status(self, message):
        """
        Sends a string status message to OSC hosts, using the address /status.
        Also prints the message to the console.
        """
        # Make sure message is a string
        if not isinstance(message, str):
            raise Exception(f'message is not a string ({message})')

        msg = OscMessageBuilder(address='/status')
        msg.add_arg(str(message))
        msg = msg.build()
        self._osc_send_function(msg)

        print(message)

    def connect_keyboard_midi_port(self, midi_port_name):
        """
        Connect to the device with the name midi_port_name.
        Pass messages through to the Nymphes, while also processing
        some of them, or at least taking note of their values:
        - Velocity
        - Channel Aftertouch
        """

        # Disconnect from the current controller, if necessary
        #
        if self.midi_controller_connected:
            # We are already connected to a keyboard controller.
            if midi_port_name != self._midi_controller_port.name:
                # Disconnect from the current controller
                self._midi_controller_port.close()
                self._midi_controller_port = None
                self.midi_controller_connected = False
            else:
                # We are already connected to the keyboard controller
                return

        # Connect to the new port
        self._midi_controller_port = mido.open_ioport(midi_port_name)
        self.midi_controller_connected = True

        self.send_status(f'Connected midi controller {midi_port_name}')



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
    def lfo1(self):
        return self._lfo1_params

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
