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
from nymphes_osc.src import sysex_handling
from nymphes_osc.src.preset_pb2 import preset, lfo_speed_mode, lfo_sync_mode, voice_mode
from nymphes_midi.src.nymphes_midi_objects import NymphesMidi


class NymphesMidiOscBridge:
    """
    An OSC server that handles MIDI communication with the Dreadbox Nymphes synthesizer.
    Enables OSC clients to control all aspects of the Nymphes' MIDI-controllable functionality.
    """

    def __init__(self, nymphes_midi_channel, osc_in_host, osc_in_port):
        # Create NymphesMidi object
        self._nymphes_midi = NymphesMidi(print_logs_enabled=True)
        self._nymphes_midi.nymphes_midi_channel = nymphes_midi_channel

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
        self._dispatcher.map('/request_sysex_dump', self._on_osc_message_request_sysex_dump)

        # Start the OSC Server
        self._start_osc_server()

    def update(self):
        """
        This method should be called regularly.
        """
        self._nymphes_midi.update()

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
        msg = OscMessageBuilder(address='/nymphes_connected' if self._nymphes_midi.nymphes_connected else '/nymphes_disconnected')
        msg = msg.build()
        client.send(msg)

        # Send the client a list of detected non-nymphes MIDI input ports
        msg = OscMessageBuilder(address='/detected_midi_input_ports')
        for port_name in self._nymphes_midi.non_nymphes_midi_input_port_names:
            msg.add_arg(port_name)
        msg = msg.build()
        client.send(msg)

        # Send the client a list of detected non-nymphes MIDI output ports
        msg = OscMessageBuilder(address='/detected_midi_output_ports')
        for port_name in self._nymphes_midi.non_nymphes_midi_output_port_names:
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
        if self._nymphes_midi.nymphes_connected:
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
                                      [name for name in self._nymphes_midi.non_nymphes_midi_input_port_names])
        
    def _send_non_nymphes_midi_output_port_names(self):
        """
        Send a list of detected non-Nymphes MIDI output port names to all OSC clients.
        """
        self._send_osc_to_all_clients('/detected_midi_output_ports',
                                      [name for name in self._nymphes_midi.non_nymphes_midi_output_port_names])

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
        if self._nymphes_midi.nymphes_connected:
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
        self._nymphes_midi.load_preset(bank_name=args[0], preset_num=args[1], preset_type=args[2])

    def _on_osc_message_load_preset_file(self, address, *args):
        """
        An OSC message has just been received to load a preset file
        """
        # Argument 0 is the filepath
        filepath = str(args[0])

        self._nymphes_midi.load_preset_file(filepath)

        # Update our OSC clients
        #

        # Status update
        self._send_status_to_all_clients(f'loaded preset file: {filepath}')

        # Send out OSC notification
        self._send_osc_to_all_clients('/loaded_preset_file', str(filepath))

    def _on_osc_message_save_preset_file(self, address, *args):
        """
        An OSC message has just been received to save a preset file
        """
        # Argument 0 is the filepath
        filepath = str(args[0])

        # Save the file
        self._nymphes_midi.save_preset_file(filepath)

        # Status update
        self._send_status_to_all_clients(f'saved preset file: {filepath}')

        # Send out OSC notification
        self._send_osc_to_all_clients('/saved_preset_file', str(filepath))

    def _on_osc_message_mod_wheel(self, address, *args):
        """
        An OSC client has just sent a message to send a MIDI Mod Wheel message.
        """
        value = args[0]

        if self._nymphes_midi.nymphes_connected:
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

        if self._nymphes_midi.nymphes_connected:
            # Construct the MIDI message
            msg = mido.Message('aftertouch',
                               channel=self.nymphes_midi_channel,
                               value=value)

            # Send the message
            self._nymphes_midi_port.send(msg)

    def _on_osc_message_request_sysex_dump(self, address, *args):
        """
        Request a full SYSEX dump of all presets from Nymphes.
        """

        self._nymphes_midi.send_sysex_dump_request()

        # Status update
        self._send_status_to_all_clients('Requested full preset SYSEX Dump')
