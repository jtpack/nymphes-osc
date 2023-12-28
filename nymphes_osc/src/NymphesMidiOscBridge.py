import threading
import socket
from zeroconf import ServiceInfo, Zeroconf
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.osc_message_builder import OscMessageBuilder
from nymphes_midi.NymphesMidi import NymphesMidi
from nymphes_midi.NymphesPreset import NymphesPreset
from nymphes_midi.PresetEvents import PresetEvents
from nymphes_midi.MidiConnectionEvents import MidiConnectionEvents


class NymphesMidiOscBridge:
    """
    An OSC server that uses nymphes-midi to handle MIDI communication with
    the Dreadbox Nymphes synthesizer.
    Enables OSC clients to control all aspects of the Nymphes'
    MIDI-controllable functionality.
    """

    def __init__(self, nymphes_midi_channel, osc_in_host, osc_in_port):
        # Create NymphesMidi object
        self._nymphes_midi = NymphesMidi(print_logs_enabled=True)
        self._nymphes_midi.nymphes_midi_channel = nymphes_midi_channel
        self._nymphes_midi.register_for_notifications(self._on_nymphes_notification)

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
        self._dispatcher.map('/open_midi_input_port', self._on_osc_message_open_midi_input_port)
        self._dispatcher.map('/close_midi_input_port', self._on_osc_message_close_midi_input_port)
        self._dispatcher.map('/open_midi_output_port', self._on_osc_message_open_midi_output_port)
        self._dispatcher.map('/close_midi_output_port', self._on_osc_message_close_midi_output_port)
        self._dispatcher.set_default_handler(self._on_other_osc_message)

        # Start the OSC Server
        self._start_osc_server()

    def update(self):
        """
        This method should be called regularly to enable MIDI message reception
        and sending, as well as MIDI connection handling.
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
        for port_name in self._nymphes_midi.detected_midi_input_ports:
            msg.add_arg(port_name)
        msg = msg.build()
        client.send(msg)

        # Send the client a list of detected non-nymphes MIDI output ports
        msg = OscMessageBuilder(address='/detected_midi_output_ports')
        for port_name in self._nymphes_midi.detected_midi_output_ports:
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
            msg = OscMessageBuilder(address='/client_unregistered')
            msg.add_arg(ip_address_string)
            msg.add_arg(port)
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

    #
    # OSC Methods
    #

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

        # Make sure an argument was supplied
        if len(args) == 0:
            print('_on_osc_message_register_client: no arguments supplied')
            return

        client_port = int(args[0])

        print(f"Received /register_client {client_port} from {client_ip}")

        # Add the client
        self.register_osc_client(ip_address_string=client_ip, port=client_port)

    def _on_osc_message_register_client_with_ip_address(self, client_address, address, *args):
        """
        A client has requested to be registered, specifying both ip address and port.
        """
        sender_ip = client_address[0]

        # Make sure arguments were supplied
        if len(args) == 0:
            print('_on_osc_message_register_client_with_ip_address: no arguments supplied')
            return

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

        # Make sure an argument was supplied
        if len(args) == 0:
            print('_on_osc_message_unregister_client: no arguments supplied')
            return

        client_port = int(args[0])

        print(f"Received /unregister_client {client_port} from {client_ip}")

        self.unregister_osc_client(ip_address_string=client_ip, port=client_port)

    def _on_osc_message_unregister_client_with_ip_address(self, client_address, address, *args):
        """
        A client has requested to be removed
        """
        sender_ip = client_address[0]

        # Make sure arguments were supplied
        if len(args) == 0:
            print('_on_osc_message_register_client_on_osc_message_unregister_client_with_ip_address: no arguments supplied')
            return

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
        # Make sure an argument was supplied
        if len(args) == 0:
            print('_on_osc_message_mod_source: no arguments supplied')
            return

        self._nymphes_midi.set_param_int('mod_source', args[0])

    def _on_osc_message_load_preset(self, address, *args):
        """
        An OSC message has just been received to load a preset from memory
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            print('_on_osc_message_load_preset: no arguments supplied')
            return

        self._nymphes_midi.load_preset(bank_name=args[0], preset_num=args[1], preset_type=args[2])

    def _on_osc_message_load_preset_file(self, address, *args):
        """
        An OSC message has just been received to load a preset file
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            print('_on_osc_message_load_preset_file: no arguments supplied')
            return

        # Get the filepath
        filepath = str(args[0])

        # Load it
        self._nymphes_midi.load_preset_file(filepath)

        # Send status update
        self._send_status_to_all_clients(f'loaded preset file: {filepath}')

        # Send out OSC notification
        self._send_osc_to_all_clients('/loaded_preset_file', filepath)

    def _on_osc_message_save_preset_file(self, address, *args):
        """
        An OSC message has just been received to save the current
        preset as a preset file
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            print('_on_osc_message_save_preset_file: no arguments supplied')
            return

        # Get the filepath
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
        # Make sure an argument was supplied
        if len(args) == 0:
            print('_on_osc_message_mod_wheel: no arguments supplied')
            return

        self._nymphes_midi.set_mod_wheel(args[0])

    def _on_osc_message_aftertouch(self, address, *args):
        """
        An OSC client has just sent a message to send a MIDI channel aftertouch message
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            print('_on_osc_message_aftertouch: no arguments supplied')
            return

        self._nymphes_midi.set_channel_aftertouch(args[0])

    def _on_osc_message_request_sysex_dump(self, address, *args):
        """
        Request a full SYSEX dump of all presets from Nymphes.
        """
        self._nymphes_midi.send_sysex_dump_request()

        # Status update
        self._send_status_to_all_clients('Requested full preset SYSEX Dump')

    def _on_osc_message_open_midi_input_port(self, address, *args):
        """
        Open a non-Nymphes MIDI input port using its name.
        All received MIDI messages on this port will be passed through
        to Nymphes.
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            print('_on_osc_message_open_midi_input_port: no arguments supplied')
            return

        self._nymphes_midi.open_midi_input_port(args[0])
        
    def _on_osc_message_close_midi_input_port(self, address, *args):
        """
        Close a non-Nymphes MIDI input port using its name.
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            print('_on_osc_message_close_midi_input_port: no arguments supplied')
            return

        self._nymphes_midi.close_midi_input_port(args[0])

    def _on_osc_message_open_midi_output_port(self, address, *args):
        """
        Open a non-Nymphes MIDI output port using its name.
        All messages received from Nymphes will be passed to the port.
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            print('_on_osc_message_open_midi_output_port: no arguments supplied')
            return

        self._nymphes_midi.open_midi_output_port(args[0])

    def _on_osc_message_close_midi_output_port(self, address, *args):
        """
        Close a non-Nymphes MIDI output port using its name.
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            print('_on_osc_message_close_midi_output_port: no arguments supplied')
            return

        self._nymphes_midi.close_midi_output_port(args[0])

    def _on_other_osc_message(self, address, *args):
        """
        An OSC message has been received which does not match any of
        the addresses we have mapped to specific functions.
        This could be a message for setting a Nymphes parameter.
        """
        # Create a param name from the address by removing the leading slash
        # and replacing other slashes with periods
        param_name = address[1:].replace('/', '.')

        # Check whether this is a valid parameter name
        if param_name in NymphesPreset.all_param_names():
            # Make sure that and argument was supplied
            if len(args) == 0:
                print(f'_on_other_osc_message: {param_name}: no argument supplied')
                return

            # Get the value
            value = args[0]

            if isinstance(value, int):
                self._nymphes_midi.set_int_param(param_name, value)

            elif isinstance(value, float):
                self._nymphes_midi.set_float_param(param_name, value)

            else:
                raise Exception(f'Invalid value type: {type(value)}')

    def _on_nymphes_notification(self, name, value):
        """
        A notification has been received from the NymphesMIDI object.
        """

        if isinstance(name, MidiConnectionEvents):
            self._send_osc_to_all_clients(name.value, value)

        elif isinstance(name, PresetEvents):
            if isinstance(value, tuple):
                self._send_osc_to_all_clients(name.value, *value)
            else:
                self._send_osc_to_all_clients(name.value, value)

        elif name == 'velocity':
            self._send_osc_to_all_clients(name, value)

        elif name == 'aftertouch':
            self._send_osc_to_all_clients(name, value)

        elif name == 'mod_wheel':
            self._send_osc_to_all_clients(name, value)

        elif name == 'float_param':
            # Get the parameter name and value
            param_name, param_value = value

            # Send OSC message to clients
            # The address will start with a /, followed by the param name with periods
            # replaced by /
            # ie: for param_name osc.wave.value, the address will be /osc/wave/value
            self._send_osc_to_all_clients(f'/{param_name.replace(".", "/")}', float(param_value))

        elif name == 'int_param':
            param_name, param_value = value

            # Send OSC message to clients
            # The address will start with a /, followed by the param name with periods
            # replaced by /
            # ie: for param_name osc.wave.value, the address will be /osc/wave/value
            self._send_osc_to_all_clients(f'/{param_name.replace(".", "/")}', int(param_value))

        else:
            if isinstance(value, tuple):
                self._send_osc_to_all_clients(name, *value)
            else:
                self._send_osc_to_all_clients(name, value)

        print(f'Notification: {name}: {value}')

