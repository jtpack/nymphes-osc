import threading
import socket
from zeroconf import ServiceInfo, Zeroconf
from pathlib import Path
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.osc_message_builder import OscMessageBuilder
import mido
import mido.backends.rtmidi
from rtmidi import InvalidPortError
from nymphes_osc.src.parameter_classes.OscillatorParams import OscillatorParams
from nymphes_osc.src.parameter_classes.PitchParams import PitchParams
from nymphes_osc.src.parameter_classes.AmpParams import AmpParams
from nymphes_osc.src.parameter_classes.HpfParams import HpfParams
from nymphes_osc.src.parameter_classes.Lfo1Params import Lfo1Params
from nymphes_osc.src.parameter_classes.Lfo2Params import Lfo2Params
from nymphes_osc.src.parameter_classes.LpfParams import LpfParams
from nymphes_osc.src.parameter_classes.MixParams import MixParams
from nymphes_osc.src.parameter_classes.PitchFilterEnvParams import PitchFilterEnvParams
from nymphes_osc.src.parameter_classes.ReverbParams import ReverbParams
from nymphes_osc.src.parameter_classes.ControlParameter_PlayMode import ControlParameter_PlayMode
from nymphes_osc.src.parameter_classes.ControlParameter_ModSource import ControlParameter_ModSource
from nymphes_osc.src.parameter_classes.ControlParameter_Legato import ControlParameter_Legato
from nymphes_osc.src import sysex_handling
from nymphes_osc.src.preset_pb2 import preset, lfo_speed_mode, lfo_sync_mode, voice_mode


class NymphesMidiOscBridge:
    """
    An OSC server that handles MIDI communication with the Dreadbox Nymphes synthesizer.
    Enables OSC clients to control all aspects of the Nymphes' MIDI-controllable functionality.
    """

    def __init__(self, nymphes_midi_channel, osc_in_host, osc_in_port):
        # Note: MIDO uses zero-referenced midi channels, so MIDI channel 1 is
        # entered as 0
        self.nymphes_midi_channel = nymphes_midi_channel - 1

        # IP Address and Port for Incoming OSC Messages from Clients
        #
        self.in_host = osc_in_host
        self.in_port = osc_in_port

        # The OSC Server, which receives OSC messages on a background thread
        #
        self._osc_server = None
        self._osc_server_thread = None
        self._dispatcher = Dispatcher()

        # mDNS Advertisement Objects
        self._mdns_service_info = None
        self._zeroconf = None

        # OSC Clients Dictionary
        # key: A tuple: (str(hostname), int(port))
        # value: The osc client object the client
        self._osc_clients_dict = {}

        # MIDI IO port for messages to and from Nymphes
        self._nymphes_midi_port = None

        # Flag indicating whether we have an active USB MIDI
        # connection to a Dreadbox Nymphes synthesizer
        self.nymphes_connected = False

        # Timer used for detecting MIDI ports
        #
        self.midi_port_detect_timer_interval_sec = 0.5
        self._midi_port_detect_timer = threading.Timer(self.midi_port_detect_timer_interval_sec, self._detect_all_midi_ports)

        # Type of the Currently-Loaded Nymphes Preset
        # Possible values: 'user' or 'factory'
        self.curr_preset_type = None

        # Preset objects for the presets in the Nymphes' memory.
        # If a full sysex dump has been done then we will have an
        # entry for every preset. If not, then we'll only have
        # entries for the presets that have been recalled since
        # connecting to the Nymphes.
        # The dict key is a tuple. ie: For bank A, user preset 1: ('user', 'A', 1).
        # The value is a preset_pb2.preset object.
        #
        self.nymphes_presets_dict = {}

        # The key to the most-recently-loaded nymphes preset object
        self.curr_nymphes_preset_dict_key = None

        # MIDI port objects for external midi controller
        #
        self._midi_controller_input_port = None
        self._midi_controller_output_port = None

        # Flags indicating whether we are connected to an external
        # MIDI controller
        #
        self.midi_controller_input_connected = False
        self.midi_controller_output_connected = False

        # Names of Detected Non-Nymphes MIDI Ports
        #
        self._non_nymphes_midi_input_port_names = []
        self._non_nymphes_midi_output_port_names = []

        # Control Parameter Objects
        # These perform the following tasks:
        # 1) Receive MIDI Control Change messages from the Nymphes, and track
        #    the values of the parameters they represent.
        # 2) Generate and send OSC messages to update clients whenever new
        #    parameter values are received from the Nymphes.
        # 3) Receive client OSC messages which represent Nymphes control
        #    parameters, and track changes to their values.
        # 4) Generate MIDI Control Change messages and send them to the
        #    Nymphes whenever new values are received from the OSC clients.
        self._oscillator_params = OscillatorParams(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)
        self._pitch_params = PitchParams(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)
        self._amp_params = AmpParams(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)
        self._mix_params = MixParams(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)
        self._lpf_params = LpfParams(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)
        self._hpf_params = HpfParams(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)
        self._pitch_filter_env_params = PitchFilterEnvParams(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)
        self._lfo1_params = Lfo1Params(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)
        self._lfo2_params = Lfo2Params(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)
        self._reverb_params = ReverbParams(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)
        self._play_mode_parameter = ControlParameter_PlayMode(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)
        self._mod_source_parameter = ControlParameter_ModSource(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)
        self._legato_parameter = ControlParameter_Legato(self._dispatcher, self._send_osc_to_all_clients, self._nymphes_midi_cc_send_function)

        # Register for non-Control Parameter OSC messages
        #
        self._dispatcher.map('/mod_source', self._on_osc_message_mod_source)
        self._dispatcher.map('/mod_wheel', self._on_osc_message_mod_wheel)
        self._dispatcher.map('/aftertouch', self._on_osc_message_aftertouch)
        self._dispatcher.map('/load_preset', self._on_osc_message_load_preset)
        self._dispatcher.map('/load_preset_file', self._on_osc_message_load_preset_file)
        self._dispatcher.map('/save_preset_file', self._on_osc_message_save_preset_file)
        self._dispatcher.map('/register_client',
                             self._on_osc_message_register_client,
                             needs_reply_address=True)
        self._dispatcher.map('/register_client_with_ip_address',
                             self._on_osc_message_register_client_with_ip_address,
                             needs_reply_address=True)
        self._dispatcher.map('/unregister_client',
                             self._on_osc_message_unregister_client,
                             needs_reply_address=True)
        self._dispatcher.map('/unregister_client_with_ip_address',
                             self._on_osc_message_unregister_client_with_ip_address,
                             needs_reply_address=True)
        self._dispatcher.map('/connect_midi_controller_input', self._on_osc_message_connect_midi_controller_input)
        self._dispatcher.map('/disconnect_midi_controller_input', self._on_osc_message_disconnect_midi_controller_input)
        self._dispatcher.map('/connect_midi_controller_output', self._on_osc_message_connect_midi_controller_output)
        self._dispatcher.map('/disconnect_midi_controller_output', self._on_osc_message_disconnect_midi_controller_output)

        # Start the OSC Server
        self._start_osc_server()

        # Start the MIDI port detection timer
        self._midi_port_detect_timer.start()

    def register_osc_client(self, ip_address_string, port):
        """
        Add a new client to send OSC messages to.
        If the client has already been added previously, we don't add it again.
        However, we still send it the same status messages, etc that we send
        to new clients. This is because the server may run for longer than the
        clients do, and we may get a request from the same client as it is started
        up.
        """
        # Validate ip_address_string
        if not isinstance(ip_address_string, str):
            raise Exception(f'ip_address_string should be a string: {ip_address_string}')

        # Validate port
        try:
            port = int(port)
        except ValueError:
            raise Exception(f'port could not be interpreted as an integer: {port}')

        if (ip_address_string, port) not in self._osc_clients_dict.keys():
            # This is a new client.
            client = SimpleUDPClient(ip_address_string, port)

            # Store the client
            self._osc_clients_dict[(ip_address_string, port)] = client

            # Send status update
            self._send_status_to_all_clients(f'Registered client ({ip_address_string}:{port})')
        else:
            # We have already added this client.
            client = self._osc_clients_dict[(ip_address_string, port)]
            self._send_status_to_all_clients(f'Client already added ({ip_address_string}:{client._port})')

        # Send osc notification to the client
        msg = OscMessageBuilder(address='/client_registered')
        msg.add_arg(ip_address_string)
        msg.add_arg(port)
        msg = msg.build()
        client.send(msg)

        # Notify the client whether or not the Nymphes is connected
        msg = OscMessageBuilder(address='/nymphes_connected' if self.nymphes_connected else '/nymphes_disconnected')
        msg = msg.build()
        client.send(msg)

        # Notify the client whether or not a MIDI controller input port is connected
        if self.midi_controller_input_connected:
            msg = OscMessageBuilder(address='/midi_controller_input_connected')
            msg.add_arg(self._midi_controller_input_port.name)
            msg = msg.build()
            client.send(msg)
        else:
            msg = OscMessageBuilder(address='/midi_controller_input_disconnected')
            msg = msg.build()
            client.send(msg)

        # Notify the client whether or not a MIDI controller output port is connected
        if self.midi_controller_output_connected:
            msg = OscMessageBuilder(address='/midi_controller_output_connected')
            msg.add_arg(self._midi_controller_output_port.name)
            msg = msg.build()
            client.send(msg)
        else:
            msg = OscMessageBuilder(address='/midi_controller_output_disconnected')
            msg = msg.build()
            client.send(msg)

        # Send the client a list of detected non-nymphes MIDI input ports
        msg = OscMessageBuilder(address='/detected_midi_input_ports')
        for port_name in self._non_nymphes_midi_input_port_names:
            msg.add_arg(port_name)
        msg = msg.build()
        client.send(msg)

        # Send the client a list of detected non-nymphes MIDI output ports
        msg = OscMessageBuilder(address='/detected_midi_output_ports')
        for port_name in self._non_nymphes_midi_output_port_names:
            msg.add_arg(port_name)
        msg = msg.build()
        client.send(msg)

    def unregister_osc_client(self, ip_address_string, port):
        """
        Remove a client that was listening for OSC messages.
        """
        # Validate ip_address_string
        if not isinstance(ip_address_string, str):
            raise Exception(f'ip_address_string should be a string: {ip_address_string}')

        # Remove the client, if it was previously added
        if (ip_address_string, port) in self._osc_clients_dict.keys():
            # Remove the client from the collection but get a reference to
            # it so we can send it one last message confirming that it has
            # been removed
            osc_client = self._osc_clients_dict.pop((ip_address_string, port))

            # Send osc notification to the client that has been removed
            msg = OscMessageBuilder(address='/client_removed')
            msg = msg.build()
            osc_client.send(msg)

            # Status update
            self._send_status_to_all_clients(f'Removed client ({ip_address_string}:{port})')

        else:
            print(f'{ip_address_string}:{port} was not a registered client')

    def connect_midi_controller_input_port(self, port_name):
        """
        Connect to the midi input device with the name port_name.
        """
        print(f'nymphes_osc connect_midi_controller_input_port {port_name}')

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

        # Notify OSC clients that the MIDI controller input has been connected
        self._send_osc_to_all_clients('/midi_controller_input_connected', port_name)

        # Send a status update
        self._send_status_to_all_clients(f'Connected midi controller input: {port_name}')

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

        # Notify OSC clients that the MIDI controller output has been connected
        self._send_osc_to_all_clients('/midi_controller_output_connected', port_name)

        # Send a status update
        self._send_status_to_all_clients(f'Connected midi controller output: {port_name}')

    def disconnect_midi_controller_input_port(self):
        if self.midi_controller_input_connected:
            midi_controller_port_name = self._midi_controller_input_port.name
            self._midi_controller_input_port.close()
            self._midi_controller_input_port = None
            self.midi_controller_input_connected = False

            # Notify OSC clients that the MIDI controller input has disconnected
            self._send_osc_to_all_clients('/midi_controller_input_disconnected', midi_controller_port_name)

            # Send a status update
            self._send_status_to_all_clients(f'Disconnected from midi controller input: {midi_controller_port_name}')

    def disconnect_midi_controller_output_port(self):
        if self.midi_controller_output_connected:
            midi_controller_port_name = self._midi_controller_output_port.name
            self._midi_controller_output_port.close()
            self._midi_controller_output_port = None
            self.midi_controller_output_connected = False

            # Notify OSC clients that the MIDI controller output has disconnected
            self._send_osc_to_all_clients('/midi_controller_output_disconnected', midi_controller_port_name)

            # Send a status update
            self._send_status_to_all_clients(f'Disconnected from midi controller output: {midi_controller_port_name}')

    def load_preset(self, bank_name, preset_num, preset_type):
        """
        Send the Nymphes a MIDI program change message to load
        the specified preset from its internal memory.
        """
        preset_types = ['user', 'factory']
        bank_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        preset_nums = [1, 2, 3, 4, 5, 6, 7]

        # Validate the arguments
        if preset_type not in preset_types:
            raise Exception(f'Invalid preset_type: {preset_type}')

        if bank_name not in bank_names:
            raise Exception(f'Invalid bank_name: {bank_name}')

        if preset_num not in preset_nums:
            raise Exception(f'Invalid preset_num: {preset_num}')

        # Send a MIDI bank select message to let the Nymphes
        # know whethr we will be loading a user or factory preset
        self._nymphes_midi_cc_send_function(midi_cc=0, value=preset_types.index(preset_type))

        # Send a MIDI program change message to load the preset
        self._nymphes_midi_program_change_send_function(
            program=(bank_names.index(bank_name) * 7) + preset_nums.index(preset_num))

    def load_preset_file(self, filepath):
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
            self._send_status_to_all_clients('Sent sysex message')

        # Update our OSC clients
        #

        # Status update
        self._send_status_to_all_clients(f'loaded preset file: {filepath}')

        # Send out OSC notification
        self._send_osc_to_all_clients('/loaded_preset_file', str(filepath))

    def save_preset_file(self, filepath):
        # Get the current settings as a preset object
        p = self._preset_object_for_current_settings()

        # Save it to a file
        sysex_handling.save_preset_file(preset_object=p, filepath=filepath)

        # Status update
        self._send_status_to_all_clients(f'saved preset file: {filepath}')

        # Send out OSC notification
        self._send_osc_to_all_clients('/saved_preset_file', str(filepath))

    def _start_osc_server(self):
        # Create the OSC Server and start it on a background thread
        #
        self._osc_server = BlockingOSCUDPServer((self.in_host, self.in_port), self._dispatcher)
        self._osc_server_thread = threading.Thread(target=self._osc_server.serve_forever)
        self._osc_server_thread.start()

        # Advertise OSC Server on the network using mDNS
        #
        self._mdns_service_info = ServiceInfo(
            type_="_osc._udp.local.",
            name="nymphes-osc._osc._udp.local.",
            addresses=[socket.inet_aton(self.in_host)],
            port=self.in_port,
            weight=0,
            priority=0,
            properties={},
            server="nymphes-osc.local."
        )

        self._zeroconf = Zeroconf()
        self._zeroconf.register_service(info=self._mdns_service_info)

        self._send_status_to_all_clients(f'Started OSC Server at {self.in_host}:{self.in_port}')
        print(f'Advertising as {self._mdns_service_info.server}')

    def _receive_midi_messages(self):
        """
        Should be called frequently.
        """
        # Handle any incoming MIDI messages waiting for us from Nymphes
        if self.nymphes_connected:
            for midi_message in self._nymphes_midi_port.iter_pending():
                self._on_nymphes_midi_message(midi_message)

        # Handle any incoming MIDI messages waiting for us from the MIDI Controller
        if self.midi_controller_input_connected:
            for midi_message in self._midi_controller_input_port.iter_pending():
                self._on_midi_controller_message(midi_message)

    def _send_non_nymphes_midi_input_port_names(self):
        """
        Send a list of detected non-Nymphes MIDI input port names to all OSC clients.
        """
        self._send_osc_to_all_clients('/detected_midi_input_ports',
                                      [name for name in self._non_nymphes_midi_input_port_names])
        
    def _send_non_nymphes_midi_output_port_names(self):
        """
        Send a list of detected non-Nymphes MIDI output port names to all OSC clients.
        """
        self._send_osc_to_all_clients('/detected_midi_output_ports',
                                      [name for name in self._non_nymphes_midi_output_port_names])

    #
    # OSC Methods
    #

    def _build_and_send_osc_message(self, address, arguments):
        """
        :param address: The osc address including the forward slash ie: /register_client
        :param arguments: A list of arguments. Hopefully their types will all be automatically detected correctly
        :return:
        """
        msg = OscMessageBuilder(address=address)
        for argument in arguments:
            msg.add_arg(argument)
        msg = msg.build()
        self._osc_client.send(msg)

    def _send_status_to_all_clients(self, message):
        """
        Sends a string status message to OSC clients, using the address /status.
        Also prints the message to the console.
        """
        # Make sure the message is a string
        message = str(message)

        # Send to all clients
        self._send_osc_to_all_clients('/status', message)

        # Print to the console
        print(message)

    def _send_osc_to_all_clients(self, address, *args):
        """
        Creates an OSC message from the supplied address and arguments
        and sends it to all clients.
        :param address: The osc address including the forward slash ie: /register_host
        :param args: A variable number of arguments, separated by commas.
        :return:
        """
        msg = OscMessageBuilder(address=address)
        for arg in args:
            msg.add_arg(arg)
        msg = msg.build()

        for osc_client in self._osc_clients_dict.values():
            osc_client.send(msg)

        #print(f'send_osc_to_clients: {address}, {[str(arg) + " " for arg in args]}')

    #
    # OSC Message Handling Methods
    #

    def _on_osc_message_register_client(self, client_address, address, *args):
        """
        A client has requested to be registered.
        We will use its detected IP address.
        """
        client_ip = client_address[0]
        client_port = int(args[0])

        print(f"Received /register_client {client_port} from {client_ip}")

        # Add the client
        self.register_osc_client(ip_address_string=client_ip, port=client_port)

    def _on_osc_message_register_client_with_ip_address(self, client_address, address, *args):
        """
        A client has requested to be registered, specifying both ip address and port.
        """
        sender_ip = client_address[0]
        client_ip = str(args[0])
        client_port = int(args[1])

        print(f"Received /register_client_with_ip_address {client_ip} {client_port} from {sender_ip}")

        # Add the client
        self.register_osc_client(ip_address_string=client_ip, port=client_port)

    def _on_osc_message_unregister_client(self, client_address, address, *args):
        """
        A client has requested to be removed. We use the sender's IP address.
        """
        client_ip = client_address[0]
        client_port = int(args[0])

        print(f"Received /unregister_client {client_port} from {client_ip}")

        self.unregister_osc_client(ip_address_string=client_ip, port=client_port)

    def _on_osc_message_unregister_client_with_ip_address(self, client_address, address, *args):
        """
        A client has requested to be removed
        """
        sender_ip = client_address[0]
        client_ip = str(args[0])
        client_port = int(args[1])

        print(f"Received /unregister_client {client_ip} {client_port} from {sender_ip}")

        self.unregister_osc_client(ip_address_string=client_ip, port=client_port)

    def _on_osc_message_mod_source(self, address, *args):
        """
        An OSC client has just sent a message to set the mod source
        0 = 'lfo2'
        1 = 'wheel'
        2 = 'velocity'
        3 = 'aftertouch'
        """

        mod_source = args[0]

        # Send the new mod source to all parameter groups.
        #
        self._amp_params.set_mod_source(mod_source)
        self._hpf_params.set_mod_source(mod_source)
        self._lfo1_params.set_mod_source(mod_source)
        self._lfo2_params.set_mod_source(mod_source)
        self._lpf_params.set_mod_source(mod_source)
        self._mix_params.set_mod_source(mod_source)
        self._oscillator_params.set_mod_source(mod_source)
        self._pitch_filter_env_params.set_mod_source(mod_source)
        self._pitch_params.set_mod_source(mod_source)
        self._reverb_params.set_mod_source(mod_source)

        # Send the new mod source to Nymphes
        #
        if self.nymphes_connected:
            # Construct the MIDI message
            msg = mido.Message('control_change',
                               channel=self.nymphes_midi_channel,
                               control=30,
                               value=mod_source)

            # Send the message
            self._nymphes_midi_port.send(msg)

    def _on_osc_message_disconnect_midi_controller_input(self, address, *args):
        print(f'Received {address}')
        self.disconnect_midi_controller_input_port()
        
    def _on_osc_message_disconnect_midi_controller_output(self, address, *args):
        self.disconnect_midi_controller_output_port()

    def _on_osc_message_load_preset(self, address, *args):
        """
        An OSC message has just been received to load a preset from memory
        """
        self.load_preset(bank_name=args[0], preset_num=args[1], preset_type=args[2])

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
        An OSC client has just sent a message to send a MIDI Mod Wheel message.
        """
        value = args[0]

        if self.nymphes_connected:
            # Construct the MIDI message
            msg = mido.Message('control_change',
                               channel=self.nymphes_midi_channel,
                               control=1,
                               value=value)

            # Send the message
            self._nymphes_midi_port.send(msg)

    def _on_osc_message_aftertouch(self, address, *args):
        """
        An OSC client has just sent a message to send a MIDI channel aftertouch message
        """
        value = args[0]

        if self.nymphes_connected:
            # Construct the MIDI message
            msg = mido.Message('aftertouch',
                               channel=self.nymphes_midi_channel,
                               value=value)

            # Send the message
            self._nymphes_midi_port.send(msg)

    #
    # MIDI Methods
    #

    def _detect_all_midi_ports(self):
        # Automatically connect to a Nymphes synthesizer if it is detected,
        # and disconnect if no longer detected.
        self._detect_nymphes_midi_io_port()

        # Automatically detect other connected MIDI devices
        self._detect_non_nymphes_midi_input_ports()
        self._detect_non_nymphes_midi_output_ports()

        # Schedule the next run of this function
        self._midi_port_detect_timer = threading.Timer(self.midi_port_detect_timer_interval_sec, self._detect_all_midi_ports)
        self._midi_port_detect_timer.start()

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

                # Notify OSC clients
                self._send_osc_to_all_clients('/nymphes_connected')

                # Send status update
                self._send_status_to_all_clients(f'Connected to Nymphes (MIDI Port: {self._nymphes_midi_port.name})')

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

                # Notify OSC clients
                self._send_osc_to_all_clients('/nymphes_disconnected')

                # Send status update
                self._send_status_to_all_clients(f'Disconnected from Nymphes (MIDI Port: {old_nymphes_port_name})')

        except InvalidPortError:
            # Sometimes an exception is thrown when trying to get port names.
            self._send_status_to_all_clients('_detect_nymphes_midi_io_port(): ignoring error while attempting to get port names (rtmidi.InvalidPortError)')

    def _detect_non_nymphes_midi_input_ports(self):
        """
        Detect non-Nymphes MIDI input ports.
        """
        # Sometimes getting port names causes an Exception...
        try:
            # Get a list of MIDI input ports
            port_names = mido.get_input_names()

            # Find the ports with the word nymphes in their names (if they exist)
            nymphes_port_names = []
            for port_name in port_names:
                if 'nymphes' in (port_name).lower():
                    nymphes_port_names.append(port_name)

            # Get a list of non-Nymphes midi input ports
            other_midi_port_names = port_names
            for nymphes_port_name in nymphes_port_names:
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

                        # Notify OSC clients that a port has disconnected
                        self._send_osc_to_all_clients('/midi_input_port_no_longer_detected', port_name)

                        # Send status update
                        self._send_status_to_all_clients(f'MIDI input port no longer detected: {port_name}')

                        # Check whether this was our MIDI controller
                        if self.midi_controller_input_connected and self._midi_controller_input_port.name == port_name:
                            # This was the input port of our midi controller.
                            # Close the port.
                            self._midi_controller_input_port.close()

                            self._midi_controller_input_port = None

                            self.midi_controller_input_connected = False

                            # Send status update
                            self._send_status_to_all_clients(f'MIDI controller input disconnected ({port_name}')

                            # Notify OSC clients that the MIDI controller has disconnected
                            self._send_osc_to_all_clients('/midi_controller_input_disconnected', port_name)

                # Handle newly-connected MIDI ports
                for port_name in other_midi_port_names:
                    if port_name not in self._non_nymphes_midi_input_port_names:
                        # This port has just been connected.
                        self._non_nymphes_midi_input_port_names.append(port_name)

                        # Notify OSC clients that a new MIDI port has been detected
                        self._send_osc_to_all_clients('/midi_input_port_detected', port_name)

                        # Send status update
                        self._send_status_to_all_clients(f'MIDI input port detected: {port_name}')

                # Send the new list of detected ports to all OSC clients
                self._send_non_nymphes_midi_input_port_names()

        except InvalidPortError:
            # Sometimes an exception is thrown when trying to get port names.
            self._send_status_to_all_clients('ignoring error while attempting to get input port names (rtmidi.InvalidPortError)')
            
    def _detect_non_nymphes_midi_output_ports(self):
        """
        Detect non-Nymphes MIDI output ports.
        """
        # Sometimes getting port names causes an Exception...
        try:
            # Get a list of MIDI output ports
            port_names = mido.get_output_names()

            # Find the ports with the word nymphes in their names (if they exist)
            nymphes_port_names = []
            for port_name in port_names:
                if 'nymphes' in (port_name).lower():
                    nymphes_port_names.append(port_name)

            # Get a list of non-Nymphes midi output ports
            other_midi_port_names = port_names
            for nymphes_port_name in nymphes_port_names:
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

                        # Notify OSC clients that a port has disconnected
                        self._send_osc_to_all_clients('/midi_output_port_no_longer_detected', port_name)

                        # Send status update
                        self._send_status_to_all_clients(f'MIDI output port no longer detected: {port_name}')

                        # Check whether this was our MIDI controller
                        if self.midi_controller_output_connected and self._midi_controller_output_port.name == port_name:
                            # This was the output port of our midi controller.
                            # Close the port.
                            self._midi_controller_output_port.close()

                            self._midi_controller_output_port = None

                            self.midi_controller_output_connected = False

                            # Send status update
                            self._send_status_to_all_clients(f'MIDI controller output disconnected ({port_name}')

                            # Notify OSC clients that the MIDI controller has disconnected
                            self._send_osc_to_all_clients('/midi_controller_output_disconnected', port_name)

                # Handle newly-connected MIDI ports
                for port_name in other_midi_port_names:
                    if port_name not in self._non_nymphes_midi_output_port_names:
                        # This port has just been connected.
                        self._non_nymphes_midi_output_port_names.append(port_name)

                        # Notify OSC clients that a new MIDI port has been detected
                        self._send_osc_to_all_clients('/midi_output_port_detected', port_name)

                        # Send status update
                        self._send_status_to_all_clients(f'MIDI output port detected: {port_name}')

                # Send the new list of detected ports to all OSC clients
                self._send_non_nymphes_midi_output_port_names()

        except InvalidPortError:
            # Sometimes an exception is thrown when trying to get port names.
            self._send_status_to_all_clients('ignoring error while attempting to get output port names (rtmidi.InvalidPortError)')

    def _nymphes_midi_cc_send_function(self, midi_cc, value):
        """
        A function used to send a MIDI CC message to the Nymphes synthesizer.
        Every member object in NymphesOscController is given a reference
        to this function so it can send MIDI CC messages.
        """
        if self.nymphes_connected:
            # Construct the MIDI message
            msg = mido.Message('control_change', channel=self.nymphes_midi_channel, control=midi_cc, value=value)

            # Send the message
            self._nymphes_midi_port.send(msg)

    def _nymphes_midi_program_change_send_function(self, program):
        """
        Used to send a program change message to the Nymphes
        """
        if self.nymphes_connected:
            # Construct the MIDI message
            msg = mido.Message('program_change', channel=self.nymphes_midi_channel, program=program)

            # Send the message
            self._nymphes_midi_port.send(msg)

    def _on_nymphes_midi_message(self, midi_message):
        """
        To be called by the nymphes midi port when new midi messages are received
        """
        # Handle MIDI Control Change Messages
        #
        if midi_message.is_cc() and midi_message.channel == self.nymphes_midi_channel:
            # Handle Bank MSB message
            # This indicates user or factory preset type
            if midi_message.control == 0:
                self._on_midi_message_bank_select(midi_message.value)

            # Handle mod source control message
            elif midi_message.control == 30:
                self._on_midi_message_mod_source(midi_message.value)

            # Handle control parameter message
            else:
                if self._amp_params.on_midi_message(midi_message):
                    return
                if self._hpf_params.on_midi_message(midi_message):
                    return
                if self._lfo1_params.on_midi_message(midi_message):
                    return
                if self._lfo2_params.on_midi_message(midi_message):
                    return
                if self._lpf_params.on_midi_message(midi_message):
                    return
                if self._mix_params.on_midi_message(midi_message):
                    return
                if self._oscillator_params.on_midi_message(midi_message):
                    return
                if self._pitch_filter_env_params.on_midi_message(midi_message):
                    return
                if self._pitch_params.on_midi_message(midi_message):
                    return
                if self._reverb_params.on_midi_message(midi_message):
                    return
                if self._play_mode_parameter.on_midi_message(midi_message):
                    return
                if self._mod_source_parameter.on_midi_message(midi_message):
                    return
                if self._legato_parameter.on_midi_message(midi_message):
                    return

                print(f'Unhandled MIDI CC message from Nymphes: Ch: {midi_message.channel}, CC {midi_message.control}, Value {midi_message.value}')

        elif midi_message.type == 'sysex':
            self._on_nymphes_sysex_message(midi_message)

        elif midi_message.type == 'program_change' and midi_message.channel == self.nymphes_midi_channel:
            # self._on_midi_message_program_change(midi_message.program)
            pass

        else:
            # Some other unhandled midi message was received
            self._send_status_to_all_clients(f'Unhandled MIDI message received from Nymphes on channel {midi_message.channel}: {midi_message}')

    def _on_nymphes_sysex_message(self, midi_message):
        """
        A sysex message has been received from the Nymphes.
        Try to interpret it as a preset.
        """
        p, preset_import_type, preset_type, bank_name, preset_num = \
            sysex_handling.preset_from_sysex_data(midi_message.data)

        # Save the preset as a file so we can examine it
        filepath = Path('/Users/Jtpack2/curr_preset.preset')
        sysex_handling.save_preset_file(p, filepath)

        print(f'Stored preset as {filepath}')

        # Store a copy of the preset
        preset_key = (preset_type, bank_name, preset_num)
        self.nymphes_presets_dict[preset_key] = p

        # Also store the dict key of the current preset
        self.curr_nymphes_preset_dict_key = preset_key

        # Prepare status update message
        status_message = 'Nymphes Preset Received: '
        status_message += f'{preset_import_type.capitalize()} import, '
        status_message += f'Bank {bank_name}, '
        status_message += f'{preset_type.capitalize()} Preset '
        status_message += f'{preset_num}'
        self._send_status_to_all_clients(status_message)

        # Also send a specific loaded_preset OSC message
        self._send_osc_to_all_clients('/loaded_preset', bank_name, int(preset_num), preset_type)

    def _on_midi_controller_message(self, midi_message):
        """
        A MIDI message has been received from the MIDI controller.
        """

        # Pass the message on to the Nymphes
        if self.nymphes_connected:
            self._nymphes_midi_port.send(midi_message)

        # Pass control change messages on our MIDI channel to our control parameters
        if midi_message.is_cc() and midi_message.channel == self.nymphes_midi_channel:
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
                if self._amp_params.on_midi_message(midi_message):
                    return
                if self._hpf_params.on_midi_message(midi_message):
                    return
                if self._lfo1_params.on_midi_message(midi_message):
                    return
                if self._lfo2_params.on_midi_message(midi_message):
                    return
                if self._lpf_params.on_midi_message(midi_message):
                    return
                if self._mix_params.on_midi_message(midi_message):
                    return
                if self._oscillator_params.on_midi_message(midi_message):
                    return
                if self._pitch_filter_env_params.on_midi_message(midi_message):
                    return
                if self._pitch_params.on_midi_message(midi_message):
                    return
                if self._reverb_params.on_midi_message(midi_message):
                    return
                if self._play_mode_parameter.on_midi_message(midi_message):
                    return
                if self._mod_source_parameter.on_midi_message(midi_message):
                    return
                if self._legato_parameter.on_midi_message(midi_message):
                    return

                print(f'Unhandled MIDI CC message from MIDI Controller on channel {midi_message.channel}: CC {midi_message.control}, Value {midi_message.value}')

        elif midi_message.type == 'aftertouch' and midi_message.channel == self.nymphes_midi_channel:
            self._on_midi_message_aftertouch(midi_message.value)

        # elif midi_message.type == 'program_change' and midi_message.channel == self.midi_channel:
        #     self._on_midi_message_program_change(midi_message.program)

    def _on_midi_message_mod_source(self, mod_source):
        # Send the new mod source to all parameter groups.
        #
        self._amp_params.set_mod_source(mod_source)
        self._hpf_params.set_mod_source(mod_source)
        self._lfo1_params.set_mod_source(mod_source)
        self._lfo2_params.set_mod_source(mod_source)
        self._lpf_params.set_mod_source(mod_source)
        self._mix_params.set_mod_source(mod_source)
        self._oscillator_params.set_mod_source(mod_source)
        self._pitch_filter_env_params.set_mod_source(mod_source)
        self._pitch_params.set_mod_source(mod_source)
        self._reverb_params.set_mod_source(mod_source)

        # Send to OSC clients
        self._send_osc_to_all_clients('/mod_source', int(mod_source))

    def _on_midi_message_mod_wheel(self, mod_wheel_value):
        """
        A mod wheel MIDI message has been received from the MIDI controller.
        """
        self._send_osc_to_all_clients('/mod_wheel', mod_wheel_value)
            
    def _on_midi_message_aftertouch(self, aftertouch_value):
        """
        An aftertouch MIDI message has been received from the MIDI controller.
        """
        self._send_osc_to_all_clients('/aftertouch', aftertouch_value)

    # def _on_midi_message_program_change(self, program_num):
    #     """
    #     A MIDI program change message has just been received, either from the Nymphes
    #     or the MIDI controller.
    #     """
    #
    #     # Construct program change string
    #     bank_num = int(program_num / 7)
    #     bank_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    #     bank_name = bank_names[bank_num]
    #     preset_num = f'{(program_num % 7) + 1}'
    #     preset_type = 'User' if self.curr_preset_type == 'user' else 'Factory'

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

    def _preset_object_for_current_settings(self):
        """
        Create and return a preset object based on the Nymphes' current settings.
        """
        p = preset()

        # Parameter Values
        p.main.wave = self._oscillator_params.wave.float_value
        p.main.lvl = self._mix_params.osc.float_value
        p.main.sub = self._mix_params.sub.float_value
        p.main.noise = self._mix_params.noise.float_value
        p.main.osc_lfo = self._pitch_params.lfo1.float_value
        p.main.cut = self._lpf_params.cutoff.float_value
        p.main.reson = self._lpf_params.resonance.float_value
        p.main.cut_eg = self._lpf_params.env_depth.float_value
        p.main.a1 = self._pitch_filter_env_params.attack.float_value
        p.main.d1 = self._pitch_filter_env_params.decay.float_value
        p.main.s1 = self._pitch_filter_env_params.sustain.float_value
        p.main.r1 = self._pitch_filter_env_params.release.float_value
        p.main.lfo_rate = self._lfo1_params.rate.float_value
        p.main.lfo_wave = self._lfo1_params.wave.float_value
        p.main.pw = self._oscillator_params.pulsewidth.float_value
        p.main.glide = self._pitch_params.glide.float_value
        p.main.dtune = self._pitch_params.detune.float_value
        p.main.chord = self._pitch_params.chord.float_value
        p.main.osc_eg = self._pitch_params.env_depth.float_value
        p.main.hpf = self._hpf_params.cutoff.float_value
        p.main.track = self._lpf_params.tracking.float_value
        p.main.cut_lfo = self._lpf_params.lfo1.float_value
        p.main.a2 = self._amp_params.attack.float_value
        p.main.d2 = self._amp_params.decay.float_value
        p.main.s2 = self._amp_params.sustain.float_value
        p.main.r2 = self._amp_params.release.float_value
        p.main.lfo_delay = self._lfo1_params.delay.float_value
        p.main.lfo_fade = self._lfo1_params.fade.float_value

        p.reverb.size = self._reverb_params.size.float_value
        p.reverb.decay = self._reverb_params.decay.float_value
        p.reverb.filter = self._reverb_params.filter.float_value
        p.reverb.mix = self._reverb_params.mix.float_value

        # Modulation Matrix Values
        #

        # LFO2
        p.lfo_2.wave = self._oscillator_params.wave.mod.lfo2_float_value
        p.lfo_2.lvl = self._mix_params.osc.mod.lfo2_float_value
        p.lfo_2.sub = self._mix_params.sub.mod.lfo2_float_value
        p.lfo_2.noise = self._mix_params.noise.mod.lfo2_float_value
        p.lfo_2.osc_lfo = self._pitch_params.lfo1.mod.lfo2_float_value
        p.lfo_2.cut = self._lpf_params.cutoff.mod.lfo2_float_value
        p.lfo_2.reson = self._lpf_params.resonance.mod.lfo2_float_value
        p.lfo_2.cut_eg = self._lpf_params.env_depth.mod.lfo2_float_value
        p.lfo_2.a1 = self._pitch_filter_env_params.attack.mod.lfo2_float_value
        p.lfo_2.d1 = self._pitch_filter_env_params.decay.mod.lfo2_float_value
        p.lfo_2.s1 = self._pitch_filter_env_params.sustain.mod.lfo2_float_value
        p.lfo_2.r1 = self._pitch_filter_env_params.release.mod.lfo2_float_value
        p.lfo_2.lfo_rate = self._lfo1_params.rate.mod.lfo2_float_value
        p.lfo_2.lfo_wave = self._lfo1_params.wave.mod.lfo2_float_value
        p.lfo_2.pw = self._oscillator_params.pulsewidth.mod.lfo2_float_value
        p.lfo_2.glide = self._pitch_params.glide.mod.lfo2_float_value
        p.lfo_2.dtune = self._pitch_params.detune.mod.lfo2_float_value
        p.lfo_2.chord = self._pitch_params.chord.mod.lfo2_float_value
        p.lfo_2.osc_eg = self._pitch_params.env_depth.mod.lfo2_float_value
        p.lfo_2.hpf = self._hpf_params.cutoff.mod.lfo2_float_value
        p.lfo_2.track = self._lpf_params.tracking.mod.lfo2_float_value
        p.lfo_2.cut_lfo = self._lpf_params.lfo1.mod.lfo2_float_value
        p.lfo_2.a2 = self._amp_params.attack.mod.lfo2_float_value
        p.lfo_2.d2 = self._amp_params.decay.mod.lfo2_float_value
        p.lfo_2.s2 = self._amp_params.sustain.mod.lfo2_float_value
        p.lfo_2.r2 = self._amp_params.release.mod.lfo2_float_value
        p.lfo_2.lfo_delay = self._lfo1_params.delay.mod.lfo2_float_value
        p.lfo_2.lfo_fade = self._lfo1_params.fade.mod.lfo2_float_value

        # Mod Wheel
        p.mod_w.wave = self._oscillator_params.wave.mod.wheel_float_value
        p.mod_w.lvl = self._mix_params.osc.mod.wheel_float_value
        p.mod_w.sub = self._mix_params.sub.mod.wheel_float_value
        p.mod_w.noise = self._mix_params.noise.mod.wheel_float_value
        p.mod_w.osc_lfo = self._pitch_params.lfo1.mod.wheel_float_value
        p.mod_w.cut = self._lpf_params.cutoff.mod.wheel_float_value
        p.mod_w.reson = self._lpf_params.resonance.mod.wheel_float_value
        p.mod_w.cut_eg = self._lpf_params.env_depth.mod.wheel_float_value
        p.mod_w.a1 = self._pitch_filter_env_params.attack.mod.wheel_float_value
        p.mod_w.d1 = self._pitch_filter_env_params.decay.mod.wheel_float_value
        p.mod_w.s1 = self._pitch_filter_env_params.sustain.mod.wheel_float_value
        p.mod_w.r1 = self._pitch_filter_env_params.release.mod.wheel_float_value
        p.mod_w.lfo_rate = self._lfo1_params.rate.mod.wheel_float_value
        p.mod_w.lfo_wave = self._lfo1_params.wave.mod.wheel_float_value
        p.mod_w.pw = self._oscillator_params.pulsewidth.mod.wheel_float_value
        p.mod_w.glide = self._pitch_params.glide.mod.wheel_float_value
        p.mod_w.dtune = self._pitch_params.detune.mod.wheel_float_value
        p.mod_w.chord = self._pitch_params.chord.mod.wheel_float_value
        p.mod_w.osc_eg = self._pitch_params.env_depth.mod.wheel_float_value
        p.mod_w.hpf = self._hpf_params.cutoff.mod.wheel_float_value
        p.mod_w.track = self._lpf_params.tracking.mod.wheel_float_value
        p.mod_w.cut_lfo = self._lpf_params.lfo1.mod.wheel_float_value
        p.mod_w.a2 = self._amp_params.attack.mod.wheel_float_value
        p.mod_w.d2 = self._amp_params.decay.mod.wheel_float_value
        p.mod_w.s2 = self._amp_params.sustain.mod.wheel_float_value
        p.mod_w.r2 = self._amp_params.release.mod.wheel_float_value
        p.mod_w.lfo_delay = self._lfo1_params.delay.mod.wheel_float_value
        p.mod_w.lfo_fade = self._lfo1_params.fade.mod.wheel_float_value

        # Velocity
        p.velo.wave = self._oscillator_params.wave.mod.velocity_float_value
        p.velo.lvl = self._mix_params.osc.mod.velocity_float_value
        p.velo.sub = self._mix_params.sub.mod.velocity_float_value
        p.velo.noise = self._mix_params.noise.mod.velocity_float_value
        p.velo.osc_lfo = self._pitch_params.lfo1.mod.velocity_float_value
        p.velo.cut = self._lpf_params.cutoff.mod.velocity_float_value
        p.velo.reson = self._lpf_params.resonance.mod.velocity_float_value
        p.velo.cut_eg = self._lpf_params.env_depth.mod.velocity_float_value
        p.velo.a1 = self._pitch_filter_env_params.attack.mod.velocity_float_value
        p.velo.d1 = self._pitch_filter_env_params.decay.mod.velocity_float_value
        p.velo.s1 = self._pitch_filter_env_params.sustain.mod.velocity_float_value
        p.velo.r1 = self._pitch_filter_env_params.release.mod.velocity_float_value
        p.velo.lfo_rate = self._lfo1_params.rate.mod.velocity_float_value
        p.velo.lfo_wave = self._lfo1_params.wave.mod.velocity_float_value
        p.velo.pw = self._oscillator_params.pulsewidth.mod.velocity_float_value
        p.velo.glide = self._pitch_params.glide.mod.velocity_float_value
        p.velo.dtune = self._pitch_params.detune.mod.velocity_float_value
        p.velo.chord = self._pitch_params.chord.mod.velocity_float_value
        p.velo.osc_eg = self._pitch_params.env_depth.mod.velocity_float_value
        p.velo.hpf = self._hpf_params.cutoff.mod.velocity_float_value
        p.velo.track = self._lpf_params.tracking.mod.velocity_float_value
        p.velo.cut_lfo = self._lpf_params.lfo1.mod.velocity_float_value
        p.velo.a2 = self._amp_params.attack.mod.velocity_float_value
        p.velo.d2 = self._amp_params.decay.mod.velocity_float_value
        p.velo.s2 = self._amp_params.sustain.mod.velocity_float_value
        p.velo.r2 = self._amp_params.release.mod.velocity_float_value
        p.velo.lfo_delay = self._lfo1_params.delay.mod.velocity_float_value
        p.velo.lfo_fade = self._lfo1_params.fade.mod.velocity_float_value

        # Aftertouch
        p.after.wave = self._oscillator_params.wave.mod.aftertouch_float_value
        p.after.lvl = self._mix_params.osc.mod.aftertouch_float_value
        p.after.sub = self._mix_params.sub.mod.aftertouch_float_value
        p.after.noise = self._mix_params.noise.mod.aftertouch_float_value
        p.after.osc_lfo = self._pitch_params.lfo1.mod.aftertouch_float_value
        p.after.cut = self._lpf_params.cutoff.mod.aftertouch_float_value
        p.after.reson = self._lpf_params.resonance.mod.aftertouch_float_value
        p.after.cut_eg = self._lpf_params.env_depth.mod.aftertouch_float_value
        p.after.a1 = self._pitch_filter_env_params.attack.mod.aftertouch_float_value
        p.after.d1 = self._pitch_filter_env_params.decay.mod.aftertouch_float_value
        p.after.s1 = self._pitch_filter_env_params.sustain.mod.aftertouch_float_value
        p.after.r1 = self._pitch_filter_env_params.release.mod.aftertouch_float_value
        p.after.lfo_rate = self._lfo1_params.rate.mod.aftertouch_float_value
        p.after.lfo_wave = self._lfo1_params.wave.mod.aftertouch_float_value
        p.after.pw = self._oscillator_params.pulsewidth.mod.aftertouch_float_value
        p.after.glide = self._pitch_params.glide.mod.aftertouch_float_value
        p.after.dtune = self._pitch_params.detune.mod.aftertouch_float_value
        p.after.chord = self._pitch_params.chord.mod.aftertouch_float_value
        p.after.osc_eg = self._pitch_params.env_depth.mod.aftertouch_float_value
        p.after.hpf = self._hpf_params.cutoff.mod.aftertouch_float_value
        p.after.track = self._lpf_params.tracking.mod.aftertouch_float_value
        p.after.cut_lfo = self._lpf_params.lfo1.mod.aftertouch_float_value
        p.after.a2 = self._amp_params.attack.mod.aftertouch_float_value
        p.after.d2 = self._amp_params.decay.mod.aftertouch_float_value
        p.after.s2 = self._amp_params.sustain.mod.aftertouch_float_value
        p.after.r2 = self._amp_params.release.mod.aftertouch_float_value
        p.after.lfo_delay = self._lfo1_params.delay.mod.aftertouch_float_value
        p.after.lfo_fade = self._lfo1_params.fade.mod.aftertouch_float_value

        # LFO1 Settings
        # Speed Mode
        if self._lfo1_params.type.string_value == 'bpm':
            p.lfo_settings.lfo_1_speed_mode = lfo_speed_mode.bpm
        elif self._lfo1_params.type.string_value == 'low':
            p.lfo_settings.lfo_1_speed_mode = lfo_speed_mode.slow
        elif self._lfo1_params.type.string_value == 'high':
            p.lfo_settings.lfo_1_speed_mode = lfo_speed_mode.fast
        elif self._lfo1_params.type.string_value == 'track':
            p.lfo_settings.lfo_1_speed_mode = lfo_speed_mode.tracking

        # Sync Mode
        if self._lfo1_params.key_sync.value:
            p.lfo_settings.lfo_1_sync_mode = lfo_sync_mode.key_synced
        else:
            p.lfo_settings.lfo_1_sync_mode = lfo_sync_mode.free

        # LFO2 Settings
        # Speed Mode
        if self._lfo2_params.type.string_value == 'bpm':
            p.lfo_settings.lfo_2_speed_mode = lfo_speed_mode.bpm
        elif self._lfo2_params.type.string_value == 'low':
            p.lfo_settings.lfo_2_speed_mode = lfo_speed_mode.slow
        elif self._lfo2_params.type.string_value == 'high':
            p.lfo_settings.lfo_2_speed_mode = lfo_speed_mode.fast
        elif self._lfo2_params.type.string_value == 'track':
            p.lfo_settings.lfo_2_speed_mode = lfo_speed_mode.tracking

        # Sync Mode
        if self._lfo2_params.key_sync.value:
            p.lfo_settings.lfo_2_sync_mode = lfo_sync_mode.key_synced
        else:
            p.lfo_settings.lfo_2_sync_mode = lfo_sync_mode.free

        # Legato
        p.legato = self._legato_parameter.value

        # Voice Mode
        if self._play_mode_parameter.string_value == 'polyphonic':
            p.voice_mode = voice_mode.poly
        elif self._play_mode_parameter.string_value == 'unison-6':
            p.voice_mode = voice_mode.uni_6
        elif self._play_mode_parameter.string_value == 'unison-4':
            p.voice_mode = voice_mode.uni_4
        elif self._play_mode_parameter.string_value == 'triphonic':
            p.voice_mode = voice_mode.uni_3
        elif self._play_mode_parameter.string_value == 'duophonic':
            p.voice_mode = voice_mode.uni_2
        elif self._play_mode_parameter.string_value == 'monophonic':
            p.voice_mode = voice_mode.mono

        # TODO: Implement Chords
        # Chord Settings
        p.chord_1.root = 0
        p.chord_1.semi_1 = 0
        p.chord_1.semi_2 = 0
        p.chord_1.semi_3 = 0
        p.chord_1.semi_4 = 0
        p.chord_1.semi_5 = 0

        p.chord_2.root = 0
        p.chord_2.semi_1 = 0
        p.chord_2.semi_2 = 0
        p.chord_2.semi_3 = 0
        p.chord_2.semi_4 = 0
        p.chord_2.semi_5 = 0

        p.chord_3.root = 0
        p.chord_3.semi_1 = 0
        p.chord_3.semi_2 = 0
        p.chord_3.semi_3 = 0
        p.chord_3.semi_4 = 0
        p.chord_3.semi_5 = 0

        p.chord_4.root = 0
        p.chord_4.semi_1 = 0
        p.chord_4.semi_2 = 0
        p.chord_4.semi_3 = 0
        p.chord_4.semi_4 = 0
        p.chord_4.semi_5 = 0

        p.chord_5.root = 0
        p.chord_5.semi_1 = 0
        p.chord_5.semi_2 = 0
        p.chord_5.semi_3 = 0
        p.chord_5.semi_4 = 0
        p.chord_5.semi_5 = 0

        p.chord_6.root = 0
        p.chord_6.semi_1 = 0
        p.chord_6.semi_2 = 0
        p.chord_6.semi_3 = 0
        p.chord_6.semi_4 = 0
        p.chord_6.semi_5 = 0

        p.chord_7.root = 0
        p.chord_7.semi_1 = 0
        p.chord_7.semi_2 = 0
        p.chord_7.semi_3 = 0
        p.chord_7.semi_4 = 0
        p.chord_7.semi_5 = 0

        p.chord_8.root = 0
        p.chord_8.semi_1 = 0
        p.chord_8.semi_2 = 0
        p.chord_8.semi_3 = 0
        p.chord_8.semi_4 = 0
        p.chord_8.semi_5 = 0

        # Extra LFO Parameters
        # LFO 2 targeting LFO 1
        p.extra_lfo_2.lfo_1_rate = self._lfo1_params.rate.mod.lfo2_float_value
        p.extra_lfo_2.lfo_1_wave = self._lfo1_params.wave.mod.lfo2_float_value
        p.extra_lfo_2.lfo_1_delay = self._lfo1_params.delay.mod.lfo2_float_value
        p.extra_lfo_2.lfo_1_fade = self._lfo1_params.fade.mod.lfo2_float_value

        # LFO 2 targeting itself
        p.extra_lfo_2.lfo_2_rate = self._lfo2_params.rate.mod.lfo2_float_value
        p.extra_lfo_2.lfo_2_wave = self._lfo2_params.wave.mod.lfo2_float_value
        p.extra_lfo_2.lfo_2_delay = self._lfo2_params.delay.mod.lfo2_float_value
        p.extra_lfo_2.lfo_2_fade = self._lfo2_params.fade.mod.lfo2_float_value

        # "Extra Modulation Parameters",
        # ie: Modulation Matrix Targeting LFO2
        p.extra_mod_w.lfo_2_rate = self._lfo2_params.rate.mod.wheel_float_value
        p.extra_mod_w.lfo_2_wave = self._lfo2_params.wave.mod.wheel_float_value
        p.extra_mod_w.lfo_2_delay = self._lfo2_params.delay.mod.wheel_float_value
        p.extra_mod_w.lfo_2_fade = self._lfo2_params.fade.mod.wheel_float_value

        p.extra_velo.lfo_2_rate = self._lfo2_params.rate.mod.velocity_float_value
        p.extra_velo.lfo_2_wave = self._lfo2_params.wave.mod.velocity_float_value
        p.extra_velo.lfo_2_delay = self._lfo2_params.delay.mod.velocity_float_value
        p.extra_velo.lfo_2_fade = self._lfo2_params.fade.mod.velocity_float_value

        p.extra_after.lfo_2_rate = self._lfo2_params.rate.mod.aftertouch_float_value
        p.extra_after.lfo_2_wave = self._lfo2_params.wave.mod.aftertouch_float_value
        p.extra_after.lfo_2_delay = self._lfo2_params.delay.mod.aftertouch_float_value
        p.extra_after.lfo_2_fade = self._lfo2_params.fade.mod.aftertouch_float_value

        p.amp_level = self._amp_params.level.float_value

        return p
