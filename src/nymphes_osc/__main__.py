import logging

from nymphes_osc.NymphesOSC import NymphesOSC
import time
import argparse
from pathlib import Path

app_version_string = '1.0.1'


def main():
    # Get logger
    logger = logging.getLogger('nymphes-osc.main')

    #
    # Handle command-line arguments
    #

    parser = argparse.ArgumentParser()

    # Server Host
    # This is optional. If not supplied, then the local
    # IP will be detected and used
    parser.add_argument(
        '--server_host',
        help='Optional. The hostname or IP address to use when listening for incoming OSC messages. If not supplied, then the local IP address is detected and used'
    )

    # Server Port
    # This is optional. If not supplied, then 1237 will be used
    parser.add_argument(
        '--server_port',
        type=int,
        default=1237,
        help='Optional. The port to use when listening for incoming OSC messages. Defaults to 1237.'
    )

    # Client Host
    # This is optional. If not supplied, then the server
    # will wait for clients to register
    parser.add_argument(
        '--client_host',
        help='Optional. The hostname or IP address to use for the OSC client. If not supplied, then the server will wait for clients to register themselves.'
    )

    # Client Port
    # This is optional. If not supplied, then the server
    # will wait for clients to register themselves
    parser.add_argument(
        '--client_port',
        type=int,
        help='Optional. The port to use for the OSC client. If not supplied, then the server will wait for clients to register themselves.'
    )

    parser.add_argument(
        '--midi_channel',
        type=int,
        default=1,
        help='Optional. MIDI Channel that Nymphes is set to use. 1 to 16. Defaults to 1.'
    )

    parser.add_argument(
        '--use_mdns',
        action='store_true',
        help='Optional. If this flag is present, then use mDNS to advertise as an OSC server on the network.'
    )

    parser.add_argument(
        '--mdns_name',
        default='nymphes-osc',
        help='Optional. Use this to specify a custom mdns name.'
    )

    parser.add_argument(
        '--osc_log_level',
        default='info',
        choices={'critical', 'error', 'warning', 'info', 'debug'},
        help='Optional. Sets the log level for NymphesOSC'
    )

    parser.add_argument(
        '--midi_log_level',
        default='info',
        choices={'critical', 'error', 'warning', 'info', 'debug'},
        help='Optional. Sets the log level for NymphesMIDI'
    )

    parser.add_argument(
        '--presets_directory_path',
        default='',
        help='Optional. The path for preset files'
    )

    args = parser.parse_args()

    if args.presets_directory_path == '':
        presets_directory_path = None
    else:
        presets_directory_path = Path(args.presets_directory_path)

    logger.info(f'***** Starting nymphes-osc {app_version_string} *****')

    #
    # Create the Nymphes OSC Controller
    #
    nymphes_osc = NymphesOSC(
        nymphes_midi_channel=args.midi_channel,
        server_port=args.server_port,
        server_host=args.server_host,
        client_port=args.client_port,
        client_host=args.client_host,
        use_mdns=args.use_mdns,
        mdns_name=args.mdns_name,
        osc_log_level=log_level_for_name(args.osc_log_level),
        midi_log_level=log_level_for_name(args.midi_log_level),
        presets_directory_path=presets_directory_path
    )

    #
    # Stay running until manually stopped
    #
    try:
        while True:
            nymphes_osc.update()
            time.sleep(0.0001)
    except KeyboardInterrupt:
        logger.warning(f'nymphes-osc is about to close')
        nymphes_osc.stop_osc_server()


def log_level_for_name(name):
    if name == 'critical':
        return logging.CRITICAL
    elif name == 'error':
        return logging.ERROR
    elif name == 'warning':
        return logging.WARNING
    elif name == 'info':
        return logging.INFO
    elif name == 'debug':
        return logging.DEBUG
    else:
        raise Exception(f'Invalid log level: {name}')


if __name__ == '__main__':
    main()


