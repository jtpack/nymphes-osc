import logging

from nymphes_osc.NymphesOSC import NymphesOSC
import time
import argparse


def main():
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
        '-m', '--midi_channel',
        type=int,
        default=1,
        help='Optional. MIDI Channel that Nymphes is set to use. 1 to 16. Defaults to 1.'
    )

    parser.add_argument(
        '--mdns_name',
        default=None,
        help='Optional. If supplied, then use mDNS to advertise on the network with this name'
    )

    parser.add_argument(
        '--osc_log_level',
        default='WARNING',
        choices={'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'},
        help='Optional. Sets the log level for NymphesOSC'
    )

    parser.add_argument(
        '--midi_log_level',
        default='WARNING',
        choices={'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'},
        help='Optional. Sets the log level for NymphesMIDI'
    )

    args = parser.parse_args()

    #
    # Create the Nymphes OSC Controller
    #
    nymphes_osc = NymphesOSC(nymphes_midi_channel=args.midi_channel, server_port=args.server_port,
                             server_host=args.server_host, client_port=args.client_port, client_host=args.client_host,
                             mdns_name=args.mdns_name)

    #
    # Stay running until manually stopped
    #
    while True:
        nymphes_osc.update()
        time.sleep(0.0001)

def log_level_for_name(name):
    if name == 'CRITICAL':
        return logging.CRITICAL
    elif name == 'ERROR':
        return logging.ERROR
    elif name == 'WARNING':
        return logging.WARNING
    elif name == 'INFO':
        return logging.INFO
    elif name == 'DEBUG':
        return logging.DEBUG
    else:
        raise Exception(f'Invalid log level: {name}')


if __name__ == '__main__':
    main()
