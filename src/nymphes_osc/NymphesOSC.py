import threading
import socket
from zeroconf import ServiceInfo, Zeroconf
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.osc_message_builder import OscMessageBuilder
from nymphes_midi.NymphesMIDI import NymphesMIDI
from nymphes_midi.NymphesPreset import NymphesPreset
from nymphes_midi.PresetEvents import PresetEvents
from nymphes_midi.MidiConnectionEvents import MidiConnectionEvents
from nymphes_osc.file_locations import get_data_files_directory_path
import netifaces
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import platform


#
# Logging
#

logger = logging.getLogger('nymphes-osc')
logger.setLevel(logging.DEBUG)

log_formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Logging to console
#
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

#
# Logging to a file
#

# Create data files directory if necessary
data_files_directory_path = get_data_files_directory_path()
if not data_files_directory_path.exists():
    try:
        data_files_directory_path.mkdir()
        logger.info(f'Created data files directory at {data_files_directory_path}')

    except Exception as e:
        logger.critical(f'Failed to create data files directory at {data_files_directory_path}: {e}')

# Create logs directory if necessary
logs_directory_path = data_files_directory_path / 'logs'
if not logs_directory_path.exists():
    try:
        logs_directory_path.mkdir()
        logger.info(f'Created logs directory at {logs_directory_path}')

    except Exception as e:
        logger.critical(f'Failed to create data files directory at {logs_directory_path}: {e}')

file_handler = logging.FileHandler(logs_directory_path / 'log.txt', mode='w')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)


def osc_address_from_parameter_name(parameter_name):
    return f"/{parameter_name.replace('.', '/')}"

def parameter_name_from_osc_address(osc_address):
    return osc_address[1:].replace('/', '.')


class NymphesOSC:
    """
    An OSC server that uses NymphesMidi to handle MIDI communication with
    the Dreadbox Nymphes synthesizer.
    Enables OSC clients to control all aspects of the Nymphes'
    MIDI-controllable functionality.
    """

    def __init__(
            self,
            nymphes_midi_channel=1,
            server_port=1237,
            server_host=None,
            client_port=None,
            client_host=None,
            use_mdns=False,
            mdns_name=None,
            osc_log_level=logging.DEBUG,
            midi_log_level=logging.DEBUG,
            presets_directory_path=None
    ):

        # Get logger
        self.logger = logging.getLogger('nymphes-osc.nymphes_osc')
        self.logger.setLevel(osc_log_level)

        self.logger.info(f'nymphes_midi_channel: {nymphes_midi_channel}')
        self.logger.info(f'server_port: {server_port}')
        self.logger.info(f'server_host: {server_host}')
        self.logger.info(f'client_port: {client_port}')
        self.logger.info(f'client_host: {client_host}')
        self.logger.info(f'use_mdns: {use_mdns}')
        self.logger.info(f'mdns_name: {mdns_name}')
        self.logger.info(f'nymphes_osc_log_level: {osc_log_level}')
        self.logger.info(f'nymphes_midi_log_level: {midi_log_level}')
        self.logger.info(f'presets_directory_path: {presets_directory_path}')

        # Create NymphesMidi object
        self._nymphes_midi = NymphesMIDI(
            notification_callback_function=self._on_nymphes_notification,
            log_level=midi_log_level,
            presets_directory_path=presets_directory_path
        )

        # The MIDI channel Nymphes is set to use.
        # This is an int with a range of 1 to 16.
        self._nymphes_midi.nymphes_midi_channel = nymphes_midi_channel

        # The port that the OSC server is listening on for incoming
        # messages
        self.in_port = server_port

        # The hostname or IP that the OSC server is listening on for
        # incoming messages
        self.in_host = server_host

        #
        # If None was supplied for the host, then use the local
        # IP address.
        #

        if self.in_host is None:
            self.in_host = self._get_local_ip_address()

        #
        # mDNS Advertising
        #
        self._use_mdns = use_mdns
        self._mdns_name = mdns_name

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
        self._dispatcher.map(
            '/register_client',
            self._on_osc_message_register_client,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/register_client_with_ip_address',
            self._on_osc_message_register_client_with_ip_address,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/unregister_client',
            self._on_osc_message_unregister_client,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/unregister_client_with_ip_address',
            self._on_osc_message_unregister_client_with_ip_address,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/load_preset',
            self._on_osc_message_load_preset,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/save_to_preset',
            self._on_osc_message_save_to_preset,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/load_file',
            self._on_osc_message_load_file,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/load_file_to_preset',
            self._on_osc_message_load_file_to_preset,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/save_to_file',
            self._on_osc_message_save_to_file,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/save_preset_to_file',
            self._on_osc_message_save_preset_to_file,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/load_init_file',
            self._on_osc_message_load_init_file,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/request_preset_dump',
            self._on_osc_message_request_preset_dump,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/connect_nymphes',
            self._on_osc_message_connect_nymphes,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/disconnect_nymphes',
            self._on_osc_message_disconnect_nymphes,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/connect_midi_input',
            self._on_osc_message_connect_midi_input,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/disconnect_midi_input',
            self._on_osc_message_disconnect_midi_input,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/enable_midi_feedback_suppression',
            self._on_osc_message_enable_midi_feedback_suppression,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/disable_midi_feedback_suppression',
            self._on_osc_message_disable_midi_feedback_suppression,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/connect_midi_output',
            self._on_osc_message_connect_midi_output,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/disconnect_midi_output',
            self._on_osc_message_disconnect_midi_output,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/set_nymphes_midi_channel',
            self._on_osc_message_set_nymphes_midi_channel,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/mod_wheel',
            self._on_osc_message_mod_wheel,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/aftertouch',
            self._on_osc_message_aftertouch,
            needs_reply_address=True
        )
        self._dispatcher.map(
            '/sustain_pedal',
            self._on_osc_message_sustain_pedal,
            needs_reply_address=True
        )
        self._dispatcher.set_default_handler(
            self._on_other_osc_message,
            needs_reply_address=True
        )

        # Start the OSC Server
        self._start_osc_server()

        # Register initial client, if it was supplied
        if client_host is not None and client_port is not None:
            self.register_osc_client(host=client_host, port=client_port)

    def update(self):
        """
        This method should be called regularly to enable MIDI message reception
        and sending, as well as MIDI connection handling.
        """
        self._nymphes_midi.update()

    def register_osc_client(self, host, port):
        """
        Add a new client to send OSC messages to.
        If the client has already been added previously, we don't add it again.
        However, we still send it the same status messages, etc that we send
        to new clients. This is because the server may run for longer than the
        clients do, and we may get a request from the same client as it is started
        up.
        """
        # Validate ip_address_string
        if not isinstance(host, str):
            raise Exception(f'ip_address_string should be a string: {host}')

        # Validate port
        try:
            port = int(port)
        except ValueError:
            raise Exception(f'port could not be interpreted as an integer: {port}')

        if (host, port) not in self._osc_clients_dict.keys():
            # This is a new client.
            client = SimpleUDPClient(host, port)

            # Store the client
            self._osc_clients_dict[(host, port)] = client

            # Send status update and log it
            status = f'Registered client ({host}:{port})'
            self._send_status_to_osc_clients(status)
            self.logger.info(status)
        else:
            # We have already added this client.
            client = self._osc_clients_dict[(host, port)]

            # Send status update and log it
            status = f'Client already registered ({host}:{client._port})'
            self._send_status_to_osc_clients(status)
            self.logger.info(status)

        # Send osc notification to the client
        msg = OscMessageBuilder(address='/client_registered')
        msg.add_arg(host)
        msg.add_arg(port)
        msg = msg.build()
        client.send(msg)

        # Send the presets directory path
        msg = OscMessageBuilder(address='/presets_directory_path')
        msg.add_arg(str(self._nymphes_midi.presets_directory_path))
        msg = msg.build()
        client.send(msg)

        # Send notifications for detected Nymphes MIDI input ports
        for port_name in self._nymphes_midi.detected_nymphes_midi_inputs:
            msg = OscMessageBuilder(address='/detected_nymphes_midi_input')
            msg.add_arg(port_name)
            msg = msg.build()
            client.send(msg)

        # Send notifications for detected Nymphes MIDI output ports
        for port_name in self._nymphes_midi.detected_nymphes_midi_outputs:
            msg = OscMessageBuilder(address='/detected_nymphes_midi_output')
            msg.add_arg(port_name)
            msg = msg.build()
            client.send(msg)

        # Notify the client whether the Nymphes is connected
        if self._nymphes_midi.nymphes_connected:
            msg = OscMessageBuilder(address='/nymphes_connected')
            msg.add_arg(self._nymphes_midi.nymphes_midi_ports[0])
            msg.add_arg(self._nymphes_midi.nymphes_midi_ports[1])
            msg = msg.build()
            client.send(msg)
        else:
            msg = OscMessageBuilder(address='/nymphes_disconnected')
            msg = msg.build()
            client.send(msg)
            
        # Send notifications for detected MIDI input ports
        for port_name in self._nymphes_midi.detected_midi_inputs:
            msg = OscMessageBuilder(address='/detected_midi_input')
            msg.add_arg(port_name)
            msg = msg.build()
            client.send(msg)

        # Send notifications for detected MIDI output ports
        for port_name in self._nymphes_midi.detected_midi_outputs:
            msg = OscMessageBuilder(address='/detected_midi_output')
            msg.add_arg(port_name)
            msg = msg.build()
            client.send(msg)

        # Send notifications for connected MIDI input ports
        for port_name in self._nymphes_midi.connected_midi_inputs:
            msg = OscMessageBuilder(address='/midi_input_connected')
            msg.add_arg(port_name)
            msg = msg.build()
            client.send(msg)

        # Send notifications for connected MIDI output ports
        for port_name in self._nymphes_midi.connected_midi_outputs:
            msg = OscMessageBuilder(address='/midi_output_connected')
            msg.add_arg(port_name)
            msg = msg.build()
            client.send(msg)

        # Send notification about whether MIDI feedback suppression
        # is enabled
        if self._nymphes_midi.midi_feedback_suppression_enabled:
            msg = OscMessageBuilder(address='/midi_feedback_suppression_enabled')
            msg = msg.build()
            client.send(msg)
        else:
            msg = OscMessageBuilder(address='/midi_feedback_suppression_disabled')
            msg = msg.build()
            client.send(msg)

        # If Nymphes is connected, then send the client all current
        # preset parameters.
        #
        if self._nymphes_midi.nymphes_connected:
            self._nymphes_midi.send_current_preset_notifications()

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

            # Send status update and log it
            status = f'Unregistered client ({ip_address_string}:{port})'
            self._send_status_to_osc_clients(status)
            self.logger.info(status)

        else:
            self.logger.warning(f'{ip_address_string}:{port} was not a registered client')

    def _start_osc_server(self):
        # Create the OSC Server and start it on a background thread
        #
        self._osc_server = BlockingOSCUDPServer((self.in_host, self.in_port), self._dispatcher)
        self._osc_server_thread = threading.Thread(target=self._osc_server.serve_forever)
        self._osc_server_thread.start()

        # Send status update and log it
        status = f'Started OSC Server at {self.in_host}:{self.in_port}'
        self._send_status_to_osc_clients(status)
        self.logger.info(status)

        if self._use_mdns and self._mdns_name is not None:
            try:
                # Advertise OSC Server on the network using mDNS
                #
                self._mdns_service_info = ServiceInfo(
                    type_="_osc._udp.local.",
                    name=f"{self._mdns_name}._osc._udp.local.",
                    addresses=[socket.inet_aton(self.in_host)],
                    port=self.in_port,
                    properties={'version': '0.1.0'},
                    server=f'{self._mdns_name}.local'
                )

                self._zeroconf = Zeroconf()
                self._zeroconf.register_service(info=self._mdns_service_info)

                # Send status update and log it
                status = f'Registered mDNS service as {self._mdns_service_info.server}'
                self._send_status_to_osc_clients(status)
                self.logger.info(status)

            except Exception as e:
                self.logger.warning(f'Failed to register mDNS service as {self._mdns_name} ({e})')

    def stop_osc_server(self):
        if self._osc_server is not None:
            self._osc_server.shutdown()
            self._osc_server.server_close()
            self._osc_server = None
            self._osc_server_thread.join()
            self._osc_server_thread = None
            self.logger.info("OSC Server Stopped")

        if self._zeroconf is not None:
            self._zeroconf.unregister_service(self._mdns_service_info)
            self._zeroconf.close()
            self.logger.info("mdns Closed")



    #
    # OSC Methods
    #

    def _send_status_to_osc_clients(self, message):
        """
        Sends a status message string to OSC clients, using the address /status.
        Also logs the message.
        """
        # Send to all clients
        self._send_osc_to_all_clients('/status', str(message))

    def _send_error_message_to_osc_clients(self, message, detailed_message):
        """
        Sends an error message string to OSC clients, using the address /error.
        Also logs the message.
        """
        # Send to all clients
        self._send_osc_to_all_clients('/error', str(message), str(detailed_message))

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

    #
    # OSC Message Handling Methods
    #

    def _on_osc_message_register_client(self, sender_ip, address, *args):
        """
        A client has requested to be registered.
        We will use its detected IP address.
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from {sender_ip[0]} without any arguments')
            return

        # Get the client's port
        client_port = int(args[0])

        self.logger.info(f"Received {address} {client_port} from {sender_ip[0]}")

        # Register the client
        try:
            self.register_osc_client(host=sender_ip[0], port=client_port)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to register client'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_register_client_with_ip_address(self, sender_ip, address, *args):
        """
        A client has requested to be registered, specifying both ip address and port.
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure arguments were supplied
        if len(args) == 0:
            self.logger.warning(self.logger.warning(f'Received {address} from {sender_ip[0]} without any arguments'))
            return

        try:
            # Get the client's IP address and port
            client_ip = str(args[0])
            client_port = int(args[1])

            self.logger.info(f"Received {address} {client_ip} {client_port} from {sender_ip[0]}")

            self.register_osc_client(host=client_ip, port=client_port)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to register client'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_unregister_client(self, sender_ip, address, *args):
        """
        A client has requested to be removed. We use the sender's IP address.
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from {sender_ip[0]} without any arguments')
            return

        try:
            # Get the client's port
            client_port = int(args[0])

            self.logger.info(f"Received {address} {client_port} from {sender_ip[0]}")

            self.unregister_osc_client(ip_address_string=sender_ip[0], port=client_port)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to unregister client'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_unregister_client_with_ip_address(self, sender_ip, address, *args):
        """
        A client has requested to be removed, specifying both its IP address and port.
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure arguments were supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from {sender_ip[0]} without any arguments')
            return

        try:
            # Get the client's IP address and port
            client_ip = str(args[0])
            client_port = int(args[1])

            self.logger.info(f"Received {address} {client_ip} {client_port} from {sender_ip[0]}")

            # Unregister the client
            self.unregister_osc_client(ip_address_string=client_ip, port=client_port)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to unregister client'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_load_preset(self, sender_ip, address, *args):
        """
        An OSC message has just been received to load a preset
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            preset_type = args[0]
            bank_name = args[1]
            preset_number = args[2]

            self.logger.info(f"Received {address} {preset_type} {bank_name} {preset_number} from {sender_ip[0]}")

            self._nymphes_midi.load_preset(
                preset_type=preset_type,
                bank_name=bank_name,
                preset_number=preset_number
            )

        except Exception as e:
            # Send status update and log it
            status = f'Failed to load preset'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_load_file(self, sender_ip, address, *args):
        """
        An OSC message has just been received to load a preset file
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            filepath = Path(args[0])
            self.logger.info(f'Received {address} {filepath} from {sender_ip[0]}')

            if filepath.suffix in ['.txt', '.TXT']:
                # This might be a preset file
                self._nymphes_midi.load_file(filepath=filepath)

            elif filepath.suffix in ['.syx', '.SYX']:
                # This may be a sysex file containing one or more presets
                self._nymphes_midi.load_syx_file(filepath=filepath)

            else:
                status = f'Invalid file: {filepath}'
                self._send_error_message_to_osc_clients(status, '')
                self.logger.warning(status)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to load file into current preset: {filepath}'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_save_to_preset(self, sender_ip, address, *args):
        """
        An OSC message has just been received to load the current preset settings
        into a Nymphes preset slot
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            preset_type = args[0]
            bank_name = args[1]
            preset_number = args[2]

            self.logger.info(f"Received {address} {preset_type} {bank_name} {preset_number} from {sender_ip[0]}")

            # Load the file
            self._nymphes_midi.save_to_preset(
                preset_type=preset_type,
                bank_name=bank_name,
                preset_number=preset_number
            )

        except Exception as e:
            # Send status update and log it
            status = f'Failed to load current preset into Nymphes preset slot'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_load_file_to_preset(self, sender_ip, address, *args):
        """
        An OSC message has just been received to load a file into
        a Nymphes preset slot
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            filepath = args[0]
            preset_type = args[1]
            bank_name = args[2]
            preset_number = args[3]

            self.logger.info(f"Received {address} {filepath} {preset_type} {bank_name} {preset_number} from {sender_ip[0]}")

            # Load the file
            self._nymphes_midi.load_file_to_preset(
                filepath=filepath,
                preset_type=preset_type,
                bank_name=bank_name,
                preset_number=preset_number
            )

        except Exception as e:
            # Send status update and log it
            status = f'Failed to load file into Nymphes preset slot'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_save_to_file(self, sender_ip, address, *args):
        """
        An OSC message has just been received to save the current
        preset as a file on disk.
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            filepath = args[0]

            self.logger.info(f'Received {address} {filepath} from {sender_ip[0]}')

            # Save the file
            self._nymphes_midi.save_to_file(filepath=filepath)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to save current preset to file'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_save_preset_to_file(self, sender_ip, address, *args):
        """
        An OSC message has been received to save a preset in a Nymphes memory
        slot to a file on disk.
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            filepath = args[0]
            preset_type = args[1]
            bank_name = args[2]
            preset_number = args[3]

            self.logger.info(f"Received {address} {filepath} {preset_type} {bank_name} {preset_number} from {sender_ip[0]}")

            # Save the file
            self._nymphes_midi.save_preset_to_file(
                filepath=filepath,
                preset_type=preset_type,
                bank_name=bank_name,
                preset_number=preset_number
            )

        except Exception as e:
            # Send status update and log it
            status = f'Failed to save preset from Nymphes preset slot to file'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_load_init_file(self, sender_ip, address, *args):
        """
        Load the init preset file (init.txt)
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        try:
            self.logger.info(f'Received {address} from client at {sender_ip[0]}')
            self._nymphes_midi.load_init_file()

        except Exception as e:
            # Send status update and log it
            status = f'Failed to load init preset'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_request_preset_dump(self, sender_ip, address, *args):
        """
        Request a full preset dump of all presets from Nymphes.
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        self.logger.info(f'Received {address} from client at {sender_ip[0]}')

        # Send the dump request
        self._nymphes_midi.request_preset_dump()

    def _on_osc_message_connect_midi_input(self, sender_ip, address, *args):
        """
        Connect a MIDI input port using its name
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            port_name = args[0]

            self.logger.info(f'Received {address} {port_name} from {sender_ip[0]}')

            # Connect the port
            self._nymphes_midi.connect_midi_input(port_name)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to connect MIDI Input port'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_connect_nymphes(self, sender_ip, address, *args):
        """
        Connect to Nymphes using the supplied MIDI input and output port names.
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            input_port_name = args[0]
            output_port_name = args[1]

            self.logger.info(f'Received {address} {input_port_name} {output_port_name} from {sender_ip[0]}')

            # Connect to the MIDI ports
            self._nymphes_midi.connect_nymphes(
                input_port_name=input_port_name,
                output_port_name=output_port_name
            )

        except Exception as e:
            # Send status update and log it
            status = f'Failed to connect Nymphes'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_disconnect_nymphes(self, sender_ip, address, *args):
        """
        Disconnect from Nymphes MIDI ports
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        try:
            self.logger.info(f'Received {address} from client at {sender_ip[0]}')

            # Disconnect Nymphes ports
            self._nymphes_midi.disconnect_nymphes()

        except Exception as e:
            # Send status update and log it
            status = f'Failed to disconnect Nymphes'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_disconnect_midi_input(self, sender_ip, address, *args):
        """
        Disconnect a MIDI input port using its name
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            port_name = args[0]

            self.logger.info(f'Received {address} {port_name} from {sender_ip[0]}')

            # Disconnect the port
            self._nymphes_midi.disconnect_midi_input(port_name)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to disconnect MIDI Input port'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_enable_midi_feedback_suppression(self, sender_ip, address, *args):
        """
        Enable MIDI feedback suppression
        """
        self.logger.info(f'Received {address} from client at {sender_ip[0]}')
        self._nymphes_midi.enable_midi_feedback_suppression()

    def _on_osc_message_disable_midi_feedback_suppression(self, sender_ip, address, *args):
        """
        Disable MIDI feedback suppression
        """
        self.logger.info(f'Received {address} from client at {sender_ip[0]}')
        self._nymphes_midi.disable_midi_feedback_suppression()

    def _on_osc_message_connect_midi_output(self, sender_ip, address, *args):
        """
        Connect a MIDI output port using its name
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            port_name = args[0]

            self.logger.info(f'Received {address} {port_name} from {sender_ip[0]}')

            # Connect the port
            self._nymphes_midi.connect_midi_output(port_name)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to connect MIDI Output port'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_disconnect_midi_output(self, sender_ip, address, *args):
        """
        Disconnect a non-Nymphes MIDI output port using its name
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            port_name = args[0]

            self.logger.info(f'Received {address} {port_name} from {sender_ip[0]}')

            # Disconnect the port
            self._nymphes_midi.disconnect_midi_output(port_name)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to disconnect MIDI Output port'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_set_nymphes_midi_channel(self, sender_ip, address, *args):
        """
        An OSC client has just sent a message to update the MIDI channel that
        Nymphes uses.
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            channel = args[0]

            self.logger.info(f'Received {address} {channel} from {sender_ip[0]}')

            # Set the channel
            self._nymphes_midi.nymphes_midi_channel = channel

        except Exception as e:
            # Send status update and log it
            message = f'Failed to set Nymphes MIDI channel'
            self._send_error_message_to_osc_clients(message, str(e))
            self.logger.warning(f'{message}: {e}')

    def _on_osc_message_mod_wheel(self, sender_ip, address, *args):
        """
        An OSC client has just sent a message to send a MIDI Mod Wheel message.
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            value = args[0]

            self.logger.info(f'Received {address} {value} from client at {sender_ip[0]}')

            self._nymphes_midi.set_mod_wheel(value)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to set mod wheel'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_aftertouch(self, sender_ip, address, *args):
        """
        An OSC client has just sent a message to send a MIDI channel aftertouch message
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            value = args[0]

            self.logger.info(f'Received {address} {value} from client at {sender_ip[0]}')

            self._nymphes_midi.set_channel_aftertouch(value)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to set aftertouch'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_osc_message_sustain_pedal(self, sender_ip, address, *args):
        """
        An OSC client has just sent a message to send a Sustain Pedal
        MIDI CC message
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Make sure an argument was supplied
        if len(args) == 0:
            self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
            return

        try:
            value = args[0]

            self.logger.info(f'Received {address} {value} from client at {sender_ip[0]}')

            self._nymphes_midi.set_sustain_pedal(value)

        except Exception as e:
            # Send status update and log it
            status = f'Failed to set sustain_pedal'
            self._send_error_message_to_osc_clients(status, str(e))
            self.logger.warning(f'{status}: {e}')

    def _on_other_osc_message(self, sender_ip, address, *args):
        """
        An OSC message has been received which does not match any of
        the addresses we have mapped to specific functions.
        This could be a message for setting a Nymphes parameter.
        :param sender_ip: This is the automatically-detected IP address of the sender
        :param address: (str) The OSC address of the message
        :param *args: The OSC message's arguments
        :return:
        """
        # Create a param name from the address by removing the leading slash
        # and replacing other slashes with periods
        param_name = parameter_name_from_osc_address(address)

        # Check whether this is a valid parameter name
        if param_name in NymphesPreset.all_param_names():
            #
            # The parameter name is valid
            #

            # Make sure that an argument was supplied
            if len(args) == 0:
                self.logger.warning(f'Received {address} from client at {sender_ip[0]} without any arguments')
                return

            # Get the value
            value = args[0]

            self.logger.info(f'Received {address} {value} from client at {sender_ip[0]}')

            if isinstance(value, int):
                try:
                    self._nymphes_midi.set_param(param_name, int_value=value)

                except Exception as e:
                    # Send status update and log it
                    status = f'Failed to set parameter'
                    self._send_error_message_to_osc_clients(status, str(e))
                    self.logger.warning(f'{status}: {e}')

            elif isinstance(value, float):
                try:
                    self._nymphes_midi.set_param(param_name, float_value=value)

                except Exception as e:
                    # Send status update and log it
                    status = f'Failed to set parameter'
                    self._send_error_message_to_osc_clients(status, str(e))
                    self.logger.warning(f'{status}: {e}')

            else:
                # Send status update and log it
                status = f'Invalid value type for {param_name}: {type(value)}'
                self._send_error_message_to_osc_clients(status, '')
                self.logger.warning(status)

        else:
            #
            # This is not a Nymphes parameter
            #
            # Send status update and log it
            status = f'Unknown OSC message received ({address} from client at {sender_ip[0]})'
            self._send_status_to_osc_clients(status)
            self.logger.warning(status)

    def _on_nymphes_notification(self, name, value):
        """
        A notification has been received from the NymphesMIDI object.
        :param name: (str) The name of the notification.
        :param value: The value. Its type varies by notification
        :return:
        """
        if name in ['velocity', 'aftertouch', 'mod_wheel', 'sustain_pedal']:
            #
            # This is a notification for a MIDI performance control
            #

            # Send it to OSC clients
            self._send_osc_to_all_clients(f'/{name}', value)

            # Log it
            self.logger.debug(f'{name}: {value}')

        elif name == 'float_param':
            #
            # This is a float preset parameter value.
            #

            # Get the parameter name and value
            param_name, param_value = value

            # Send OSC message to clients
            # The address will start with a /, followed by the param name with periods
            # replaced by /
            # ie: for param_name osc.wave.value, the address will be /osc/wave/value
            self._send_osc_to_all_clients(osc_address_from_parameter_name(param_name), float(param_value))

            # Log it
            self.logger.debug(f'{name}: {value}')

        elif name == 'int_param':
            param_name, param_value = value

            # Send OSC message to clients
            # The address will start with a /, followed by the param name with periods
            # replaced by /
            # ie: for param_name osc.wave.value, the address will be /osc/wave/value
            self._send_osc_to_all_clients(osc_address_from_parameter_name(param_name), int(param_value))

            # Log it
            self.logger.debug(f'{name}: {value}')

        elif name in PresetEvents.all_values():
            if isinstance(value, tuple):
                self._send_osc_to_all_clients(f'/{name}', *value)

                # Log the notification
                self.logger.info(f'{name}: {value}')

            elif value is None:
                self._send_osc_to_all_clients(f'/{name}')

                # Log the notification
                self.logger.info(f'{name}')

            else:
                self._send_osc_to_all_clients(f'/{name}', value)

                # Log the notification
                self.logger.info(f'{name}: {value}')

        elif name in MidiConnectionEvents.all_values():
            if isinstance(value, tuple):
                self._send_osc_to_all_clients(f'/{name}', *value)

                # Log the notification
                self.logger.info(f'{name}: {value}')

            elif value is None:
                self._send_osc_to_all_clients(f'/{name}')

                # Log the notification
                self.logger.info(f'{name}')

            else:
                self._send_osc_to_all_clients(f'/{name}', value)

                # Log the notification
                self.logger.info(f'{name}: {value}')

        else:
            # This is some other notification

            if isinstance(value, tuple):
                self._send_osc_to_all_clients(f'/{name}', *value)

                # Log the notification
                self.logger.info(f'{name}: {value}')

            elif value is None:
                self._send_osc_to_all_clients(f'/{name}')

                # Log the notification
                self.logger.info(f'{name}')

            else:
                self._send_osc_to_all_clients(f'/{name}', value)

                # Log the notification
                self.logger.info(f'{name}: {value}')

    def _get_local_ip_address(self):
        """
        Return the local IP address as a string.
        If no address other than 127.0.0.1 can be found, then
        return '127.0.0.1'
        :return: str
        """
        # Get a list of all network interfaces
        interfaces = netifaces.interfaces()

        for iface in interfaces:
            try:
                # Get the addresses associated with the interface
                addresses = netifaces.ifaddresses(iface)

                # Extract the IPv4 addresses (if available)
                if netifaces.AF_INET in addresses:
                    ip_info = addresses[netifaces.AF_INET][0]
                    ip_address = ip_info['addr']
                    if ip_address != '127.0.0.1':
                        return ip_address

            except Exception as e:
                self.logger.warning(f'Failed to detect local IP address ({e})')

                # Default to localhost
                return '127.0.0.1'

        # If we get here, then no IP Address other than 127.0.0.1 was found
        return '127.0.0.1'
