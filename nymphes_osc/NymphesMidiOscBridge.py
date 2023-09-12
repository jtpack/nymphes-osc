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

    def __init__(self, midi_channel, osc_in_host, osc_in_port):
        # Prepare OSC objects
        #
        self.midi_channel = midi_channel-1 # mido library is zero-referenced, so MIDI channel 1 is specified as 0
        self.in_host = osc_in_host
        self.in_port = osc_in_port

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

        # Current Nymphes preset type
        # Possible values: 'user' or 'factory'
        self.curr_preset_type = None

        # Preset objects for the presets in the Nymphes' memory.
        # If a full sysex dump has been done then we will have an
        # entry for every preset. If not, then we'll only have
        # entries for the presets that have been recalled since
        # connecting to the Nymphes.
        # The dict key is a tuple. ie: for bank A, user preset 1: ('user', 'A', 1).
        # The value is a preset_pb2.preset object.
        self.nymphes_presets = {}

        # MIDI ports for keyboard controller
        self._midi_controller_input_port = None
        self._midi_controller_output_port = None

        # Flags indicating whether we are connected to a MIDI controller's input and output
        self.midi_controller_input_connected = False
        self.midi_controller_output_connected = False

        # Lists of detected non-Nymphes midi ports
        self._non_nymphes_midi_input_port_names = []
        self._non_nymphes_midi_output_port_names = []

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
        self._dispatcher.map('/mod_source', self._on_osc_message_mod_source)
        self._dispatcher.map('/mod_wheel', self._on_osc_message_mod_wheel)
        self._dispatcher.map('/aftertouch', self._on_osc_message_aftertouch)
        self._dispatcher.map('/load_preset_file', self._on_osc_message_load_preset_file)
        self._dispatcher.map('/save_preset_file', self._on_osc_message_load_preset_file)
        self._dispatcher.map('/add_host', self._on_osc_message_add_host)
        self._dispatcher.map('/remove_host', self._on_osc_message_remove_host)
        self._dispatcher.map('/connect_midi_controller_input', self._on_osc_message_connect_midi_controller_input)
        self._dispatcher.map('/disconnect_midi_controller_input', self._on_osc_message_disconnect_midi_controller_input)
        self._dispatcher.map('/connect_midi_controller_output', self._on_osc_message_connect_midi_controller_output)
        self._dispatcher.map('/disconnect_midi_controller_output', self._on_osc_message_disconnect_midi_controller_output)

        # Start the OSC Server
        self.start_osc_server()

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

    def start_osc_server(self):
        self._osc_server = BlockingOSCUDPServer((self.in_host, self.in_port), self._dispatcher)
        self._osc_server_thread = threading.Thread(target=self._osc_server.serve_forever)
        self._osc_server_thread.start()
        
        self.send_status(f'Started OSC Server at {self.in_host}:{self.in_port}')

    def stop_osc_server(self):
        if self._osc_server is not None:
            self._osc_server.shutdown()
            self._osc_server.server_close()
            self._osc_server = None
            self._osc_server_thread.join()
            self._osc_server_thread = None
            self.send_status('Stopped OSC Server')

    def update(self):
        """
        Should be called regularly.
        """
        # Automatically connect to a Nymphes synthesizer if it is detected,
        # and disconnect if no longer detected.
        self._detect_nymphes_midi_io_port()

        # Automatically detect other connected MIDI devices
        self._detect_non_nymphes_midi_input_ports()
        self._detect_non_nymphes_midi_output_ports()

        # Handle any incoming MIDI messages waiting for us from Nymphes
        if self.nymphes_connected:
            for midi_message in self._nymphes_midi_port.iter_pending():
                self._on_nymphes_midi_message(midi_message)

        # Handle any incoming MIDI messages waiting for us from the MIDI Controller
        if self.midi_controller_input_connected:
            for midi_message in self._midi_controller_input_port.iter_pending():
                self._on_midi_controller_message(midi_message)

    def add_osc_host(self, host_name, port):
        """
        Add a new host to send OSC messages to.
        If the host has already been added previously, we don't add it again.
        However, we still send it the same status messages, etc that we send
        to new hosts. This is because the server may run for longer than the
        hosts do, and we may get a request from the same host as it is started
        up.
        """
        # Validate host_name
        if not isinstance(host_name, str):
            raise Exception(f'host_name should be a string: {host_name}')

        # Validate port
        try:
            _ = int(port)
        except ValueError:
            raise Exception(f'port could not be interpreted as an integer: {port}')

        if host_name not in self._osc_hosts.keys():
            # This is a new host.
            # Create an osc client for it.
            client = SimpleUDPClient(host_name, int(port))

            # Store the client
            self._osc_hosts[host_name] = client

            # Send status update
            self.send_status(f'Added host: {host_name} on port {int(port)}')
        else:
            # We have already added this host.
            client = self._osc_hosts[host_name]
            self.send_status(f'Host already added ({host_name} on port {client._port})')

        # Send osc notification to the host
        msg = OscMessageBuilder(address='/host_added')
        msg.add_arg(host_name)
        msg.add_arg(int(port))
        msg = msg.build()
        client.send(msg)

        # Notify the host whether or not the Nymphes is connected
        msg = OscMessageBuilder(address='/nymphes_connected' if self.nymphes_connected else '/nymphes_disconnected')
        msg = msg.build()
        client.send(msg)

        # Notify the host whether or not a MIDI controller is connected
        msg = OscMessageBuilder(address='/midi_controller_connected' if self.midi_controller_input_connected else '/midi_controller_disconnected')
        msg = msg.build()
        client.send(msg)

        # Send the host a list of detected non-nymphes MIDI input ports
        msg = OscMessageBuilder(address='/detected_midi_input_ports')
        for port_name in self._non_nymphes_midi_input_port_names:
            msg.add_arg(port_name)
        msg = msg.build()
        client.send(msg)

        # Send the host a list of detected non-nymphes MIDI output ports
        msg = OscMessageBuilder(address='/detected_midi_output_ports')
        for port_name in self._non_nymphes_midi_output_port_names:
            msg.add_arg(port_name)
        msg = msg.build()
        client.send(msg)

    def send_non_nymphes_midi_input_port_names(self):
        """
        Send a list of detected non-Nymphes MIDI input port names to all OSC hosts.
        """
        msg = OscMessageBuilder(address='/detected_midi_input_ports')
        for port_name in self._non_nymphes_midi_input_port_names:
            msg.add_arg(port_name)
        msg = msg.build()
        self._osc_send_function(msg)
        
    def send_non_nymphes_midi_output_port_names(self):
        """
        Send a list of detected non-Nymphes MIDI output port names to all OSC hosts.
        """
        msg = OscMessageBuilder(address='/detected_midi_output_ports')
        for port_name in self._non_nymphes_midi_output_port_names:
            msg.add_arg(port_name)
        msg = msg.build()
        self._osc_send_function(msg)

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

    def connect_midi_controller_input_port(self, port_name):
        """
        Connect to the midi input device with the name port_name.
        """

        # Disconnect from the current controller, if necessary
        #
        if self.midi_controller_input_connected:
            # We are already connected to a midi controller input.
            if port_name != self._midi_controller_input_port.name:
                # Disconnect from the current controller input
                self.disconnect_midi_controller_input_port()
            else:
                # We are already connected to the specified MIDI controller
                return

        # Connect to the new port
        self._midi_controller_input_port = mido.open_input(port_name)
        self.midi_controller_input_connected = True

        # Notify OSC Hosts that the MIDI controller input has been connected
        msg = OscMessageBuilder(address='/midi_controller_input_connected')
        msg.add_arg(port_name)
        msg = msg.build()
        self._osc_send_function(msg)

        # Send a status update
        self.send_status(f'Connected midi controller input: {port_name}')
        
    def connect_midi_controller_output_port(self, port_name):
        """
        Connect to the midi output device with the name port_name.
        """

        # Disconnect from the current controller, if necessary
        #
        if self.midi_controller_output_connected:
            # We are already connected to a midi controller output.
            if port_name != self._midi_controller_output_port.name:
                # Disconnect from the current controller output
                self.disconnect_midi_controller_output_port()
            else:
                # We are already connected to the specified MIDI controller
                return

        # Connect to the new port
        self._midi_controller_output_port = mido.open_output(port_name)
        self.midi_controller_output_connected = True

        # Notify OSC Hosts that the MIDI controller output has been connected
        msg = OscMessageBuilder(address='/midi_controller_output_connected')
        msg.add_arg(port_name)
        msg = msg.build()
        self._osc_send_function(msg)

        # Send a status update
        self.send_status(f'Connected midi controller output: {port_name}')

    def disconnect_midi_controller_input_port(self):
        if self.midi_controller_input_connected:
            midi_controller_port_name = self._midi_controller_input_port.name
            self._midi_controller_input_port.close()
            self._midi_controller_input_port = None
            self.midi_controller_input_connected = False

            # Notify OSC Hosts that the MIDI controller input has disconnected
            msg = OscMessageBuilder(address='/midi_controller_input_disconnected')
            msg = msg.build()
            self._osc_send_function(msg)

            # Send a status update
            self.send_status(f'Disconnected from midi controller input: {midi_controller_port_name}')
            
    def disconnect_midi_controller_output_port(self):
        if self.midi_controller_output_connected:
            midi_controller_port_name = self._midi_controller_output_port.name
            self._midi_controller_output_port.close()
            self._midi_controller_output_port = None
            self.midi_controller_output_connected = False

            # Notify OSC Hosts that the MIDI controller output has disconnected
            msg = OscMessageBuilder(address='/midi_controller_output_disconnected')
            msg = msg.build()
            self._osc_send_function(msg)

            # Send a status update
            self.send_status(f'Disconnected from midi controller output: {midi_controller_port_name}')

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

    #
    # OSC Methods
    #

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

    def _osc_send_function(self, osc_message):
        """
        A function used to send an OSC message.
        Every member object in NymphesOscController is given a reference
        to this function so it can send OSC messages.
        """
        for osc_client in self._osc_hosts.values():
            osc_client.send(osc_message)

    def _on_osc_message_add_host(self, address, *args):
        """
        A host has requested to be added
        """
        self.add_osc_host(host_name=str(args[0]), port=int(args[1]))

    def _on_osc_message_remove_host(self, address, *args):
        """
        A host has requested to be removed
        """
        self.remove_osc_host(host_name=args[0])

    def _on_osc_message_mod_source(self, address, *args):
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

    def _on_osc_message_disconnect_midi_controller_input(self, address, *args):
        self.disconnect_midi_controller_input_port()
        
    def _on_osc_message_disconnect_midi_controller_output(self, address, *args):
        self.disconnect_midi_controller_output_port()

    def _on_osc_message_load_preset_file(self, address, *args):
        """
        An OSC message has just been received to load a preset file
        """
        # Argument 0 is the filepath
        filepath = str(args[0])

        self.load_preset_file(filepath)

    def _on_osc_message_save_preset_file(self, address, *args):
        """
        An OSC message has just been received to save a preset file
        """
        # Argument 0 is the filepath
        filepath = str(args[0])

        self.save_preset_file(filepath)

    def _on_osc_message_connect_midi_controller_input(self, address, *args):
        port_name = args[0]
        self.connect_midi_controller_input_port(port_name)
        
    def _on_osc_message_connect_midi_controller_output(self, address, *args):
        port_name = args[0]
        self.connect_midi_controller_output_port(port_name)

    def _on_osc_message_mod_wheel(self, address, *args):
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

    def _on_osc_message_aftertouch(self, address, *args):
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

    #
    # MIDI Methods
    #

    def _detect_nymphes_midi_io_port(self):
        """
        Automatically connect to a Nymphes synthesizer if it is detected,
        and handle disconnection if no longer detected.
        """
        # Sometimes getting port names causes an Exception...
        try:
            # Get a list of MIDI IO ports
            port_names = mido.get_ioport_names()

            #
            # Handle Nymphes connection
            #

            # Find a port with the word nymphes in its name
            nymphes_port_name = None
            for port_name in port_names:
                if 'nymphes' in (port_name).lower():
                    nymphes_port_name = port_name

            if nymphes_port_name is not None and not self.nymphes_connected:
                # A Nymphes is connected to the computer
                # but we are not connected to it.

                # Connect to the port
                self._nymphes_midi_port = mido.open_ioport(nymphes_port_name)

                # Update connection flag
                self.nymphes_connected = True

                # Notify OSC Hosts
                msg = OscMessageBuilder(address='/nymphes_connected')
                msg = msg.build()
                self._osc_send_function(msg)

                # Send status update
                self.send_status(f'Connected to Nymphes (MIDI Port: {self._nymphes_midi_port.name})')

            if nymphes_port_name is None and self.nymphes_connected:
                # A Nymphes is not connected to the computer,
                # but we were just connected to one. It must
                # have been disconnected.

                # Close the port
                self._nymphes_midi_port.close()

                # We no longer need this port
                old_nymphes_port_name = self._nymphes_midi_port.name
                self._nymphes_midi_port = None

                # Update connection flag
                self.nymphes_connected = False

                # Notify OSC Hosts
                msg = OscMessageBuilder(address='/nymphes_disconnected')
                msg = msg.build()
                self._osc_send_function(msg)

                # Send status update
                self.send_status(f'Disconnected from Nymphes (MIDI Port: {old_nymphes_port_name})')

        except InvalidPortError:
            # Sometimes an exception is thrown when trying to get port names.
            self.send_status('_detect_nymphes_midi_io_port(): ignoring error while attempting to get port names (rtmidi.InvalidPortError)')

    def _detect_non_nymphes_midi_input_ports(self):
        """
        Detect non-Nymphes MIDI input ports.
        """
        # Sometimes getting port names causes an Exception...
        try:
            # Get a list of MIDI input ports
            port_names = mido.get_input_names()

            # Find the port with the word nymphes in its name (if it exists)
            nymphes_port_name = None
            for port_name in port_names:
                if 'nymphes' in (port_name).lower():
                    nymphes_port_name = port_name

            # Get a list of non-Nymphes midi input ports
            other_midi_port_names = port_names
            if nymphes_port_name is not None:
                other_midi_port_names.remove(nymphes_port_name)

            # Determine whether any new ports have been detected, or known ports
            # have disconnected

            if set(other_midi_port_names) != set(self._non_nymphes_midi_input_port_names):
                # There has been some kind of change to the list of detected MIDI ports.

                # Handle ports that have disconnected
                #
                for port_name in self._non_nymphes_midi_input_port_names:
                    if port_name not in other_midi_port_names:
                        # This port is no longer connected.
                        self._non_nymphes_midi_input_port_names.remove(port_name)

                        # Notify OSC Hosts that a port has disconnected
                        msg = OscMessageBuilder(address='/midi_input_port_no_longer_detected')
                        msg.add_arg(port_name)
                        msg = msg.build()
                        self._osc_send_function(msg)

                        # Send status update
                        self.send_status(f'MIDI input port no longer detected: {port_name}')

                        # Check whether this was our MIDI controller
                        if self.midi_controller_input_connected and self._midi_controller_input_port.name == port_name:
                            # This was the input port of our midi controller.
                            # Close the port.
                            self._midi_controller_input_port.close()

                            self._midi_controller_input_port = None

                            self.midi_controller_input_connected = False

                            # Send status update
                            self.send_status(f'MIDI controller input disconnected ({port_name}')

                            # Notify OSC Hosts that the MIDI controller has disconnected
                            msg = OscMessageBuilder(address='/midi_controller_input_disconnected')
                            msg.add_arg(port_name)
                            msg = msg.build()
                            self._osc_send_function(msg)

                # Handle newly-connected MIDI ports
                for port_name in other_midi_port_names:
                    if port_name not in self._non_nymphes_midi_input_port_names:
                        # This port has just been connected.
                        self._non_nymphes_midi_input_port_names.append(port_name)

                        # Notify OSC Hosts that a new MIDI port has been detected
                        msg = OscMessageBuilder(address='/midi_input_port_detected')
                        msg.add_arg(port_name)
                        msg = msg.build()
                        self._osc_send_function(msg)

                        # Send status update
                        self.send_status(f'MIDI input port detected: {port_name}')

                # Send the new list of detected ports to all OSC hosts
                self.send_non_nymphes_midi_input_port_names()

        except InvalidPortError:
            # Sometimes an exception is thrown when trying to get port names.
            self.send_status('ignoring error while attempting to get input port names (rtmidi.InvalidPortError)')
            
    def _detect_non_nymphes_midi_output_ports(self):
        """
        Detect non-Nymphes MIDI output ports.
        """
        # Sometimes getting port names causes an Exception...
        try:
            # Get a list of MIDI output ports
            port_names = mido.get_output_names()

            # Find the port with the word nymphes in its name (if it exists)
            nymphes_port_name = None
            for port_name in port_names:
                if 'nymphes' in (port_name).lower():
                    nymphes_port_name = port_name

            # Get a list of non-Nymphes midi output ports
            other_midi_port_names = port_names
            if nymphes_port_name is not None:
                other_midi_port_names.remove(nymphes_port_name)

            # Determine whether any new ports have been detected, or known ports
            # have disconnected

            if set(other_midi_port_names) != set(self._non_nymphes_midi_output_port_names):
                # There has been some kind of change to the list of detected MIDI ports.

                # Handle ports that have disconnected
                #
                for port_name in self._non_nymphes_midi_output_port_names:
                    if port_name not in other_midi_port_names:
                        # This port is no longer connected.
                        self._non_nymphes_midi_output_port_names.remove(port_name)

                        # Notify OSC Hosts that a port has disconnected
                        msg = OscMessageBuilder(address='/midi_output_port_no_longer_detected')
                        msg.add_arg(port_name)
                        msg = msg.build()
                        self._osc_send_function(msg)

                        # Send status update
                        self.send_status(f'MIDI output port no longer detected: {port_name}')

                        # Check whether this was our MIDI controller
                        if self.midi_controller_output_connected and self._midi_controller_output_port.name == port_name:
                            # This was the output port of our midi controller.
                            # Close the port.
                            self._midi_controller_output_port.close()

                            self._midi_controller_output_port = None

                            self.midi_controller_output_connected = False

                            # Send status update
                            self.send_status(f'MIDI controller output disconnected ({port_name}')

                            # Notify OSC Hosts that the MIDI controller has disconnected
                            msg = OscMessageBuilder(address='/midi_controller_output_disconnected')
                            msg.add_arg(port_name)
                            msg = msg.build()
                            self._osc_send_function(msg)

                # Handle newly-connected MIDI ports
                for port_name in other_midi_port_names:
                    if port_name not in self._non_nymphes_midi_output_port_names:
                        # This port has just been connected.
                        self._non_nymphes_midi_output_port_names.append(port_name)

                        # Notify OSC Hosts that a new MIDI port has been detected
                        msg = OscMessageBuilder(address='/midi_output_port_detected')
                        msg.add_arg(port_name)
                        msg = msg.build()
                        self._osc_send_function(msg)

                        # Send status update
                        self.send_status(f'MIDI output port detected: {port_name}')

                # Send the new list of detected ports to all OSC hosts
                self.send_non_nymphes_midi_output_port_names()

        except InvalidPortError:
            # Sometimes an exception is thrown when trying to get port names.
            self.send_status('ignoring error while attempting to get output port names (rtmidi.InvalidPortError)')

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

    def _on_nymphes_midi_message(self, midi_message):
        """
        To be called by the nymphes midi port when new midi messages are received
        """
        # Handle MIDI Control Change Messages
        #
        if midi_message.is_cc() and midi_message.channel == self.midi_channel:
            # Handle Bank MSB message
            # This indicates user or factory preset type
            if midi_message.control == 0:
                self._on_midi_message_bank_select(midi_message.value)

            # Handle mod source control message
            elif midi_message.control == 30:
                self._on_midi_message_mod_source(midi_message.value)

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

                print(f'Unhandled MIDI CC message: CC {midi_message.control}, Value {midi_message.value}')

        elif midi_message.type == 'sysex':
            self._on_nymphes_sysex_message(midi_message)

        elif midi_message.type == 'program_change' and midi_message.channel == self.midi_channel:
            self._on_midi_message_program_change(midi_message.program)

        else:
            # Some other unhandled midi message was received
            self.send_status(f'Unhandled MIDI Message Received: {midi_message}')

    def _on_nymphes_sysex_message(self, midi_message):
        """
        A sysex message has been received from the Nymphes.
        Try to interpret it as a preset.
        """
        p, preset_import_type, preset_type, bank_name, preset_number = \
            sysex_handling.preset_from_sysex_data(midi_message.data)

        if preset_import_type == 'persistent':
            # Store a copy of any persistent preset received
            self.nymphes_presets[(preset_type, bank_name, preset_number)] = p

        # Prepare status update message
        status_message = 'Nymphes Preset Received: '
        status_message += f'{preset_import_type.capitalize()} import, '
        status_message += f'Bank {bank_name}, '
        status_message += f'{preset_type.capitalize()} Preset '
        status_message += f'{preset_number}'
        self.send_status(status_message)

    def _on_midi_controller_message(self, midi_message):
        """
        A MIDI message has been received from the MIDI controller.
        """

        # Pass the message on to the Nymphes
        if self.nymphes_connected:
            self._nymphes_midi_port.send(midi_message)

        # Pass control change messages on our MIDI channel to our control parameters
        if midi_message.is_cc() and midi_message.channel == self.midi_channel:
            # Handle Bank MSB message
            # This indicates user or factory preset type
            if midi_message.control == 0:
                self._on_midi_message_bank_select(midi_message.value)

            # Handle mod source control message
            elif midi_message.control == 30:
                self._on_midi_message_mod_source(midi_message.value)

            # Handle Mod Wheel Message
            elif midi_message.control == 1:
                self._on_midi_message_mod_wheel(midi_message.value)

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

                print(f'Unhandled MIDI CC message: CC {midi_message.control}, Value {midi_message.value}')

        elif midi_message.type == 'aftertouch' and midi_message.channel == self.midi_channel:
            self._on_midi_message_aftertouch(midi_message.value)

        elif midi_message.type == 'program_change' and midi_message.channel == self.midi_channel:
            self._on_midi_message_program_change(midi_message.program)

    def _on_midi_message_mod_source(self, mod_source):
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

    def _on_midi_message_mod_wheel(self, mod_wheel_value):
        """
        A mod wheel MIDI message has been received from the MIDI controller.
        """
        msg = OscMessageBuilder(address='/mod_wheel')
        msg.add_arg(mod_wheel_value)
        msg = msg.build()
        self._osc_send_function(msg)
            
    def _on_midi_message_aftertouch(self, aftertouch_value):
        """
        An aftertouch MIDI message has been received from the MIDI controller.
        """
        msg = OscMessageBuilder(address='/aftertouch')
        msg.add_arg(aftertouch_value)
        msg = msg.build()
        self._osc_send_function(msg)

    def _on_midi_message_program_change(self, program_num):
        """
        A MIDI program change message has just been received, either from the Nymphes
        or the MIDI controller.
        """
        print(f'program_num: {program_num}')

        # Construct program change string
        bank_num = int(program_num / 7)
        bank_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        bank_name = bank_names[bank_num]
        preset_num = f'{(program_num % 7) + 1}'
        preset_type = 'User' if self.curr_preset_type == 'user' else 'Factory'
        prog_change_string = f'Bank {bank_name}, {preset_type} Preset {preset_num}'

        # Inform OSC hosts
        msg = OscMessageBuilder(address='/nymphes_program_changed')
        msg.add_arg(self.curr_preset_type)
        msg.add_arg(int(program_num))
        msg.add_arg(prog_change_string)
        msg = msg.build()
        self._osc_send_function(msg)

        self.send_status(f'Program Change: {prog_change_string}')

    def _on_midi_message_bank_select(self, bank):
        """
        A control change 0 message (Bank Select MSB) message has
        been received. This is always sent just before a program
        change message, and indicates whether the program is a
        user or factory preset.
        This is NOT the same as the Nymphes' preset banks (A-G).
        0: User
        1: Factory
        """
        # We will just store this value
        self.curr_preset_type = 'user' if bank == 0 else 'factory'
