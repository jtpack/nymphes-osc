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
        '--debug_osc',
        action='store_true',
        help='Optional. Enables logging of debug messages from NymphesOscBridge.'
    )

    parser.add_argument(
        '--debug_midi',
        action='store_true',
        help='Optional. Enables logging of debug messages from NymphesMidi.'
    )

    args = parser.parse_args()

    #
    # Create the Nymphes OSC Controller
    #
    nymphes_osc = NymphesOSC(
        nymphes_midi_channel=args.midi_channel,
        server_host=args.server_host,
        server_port=args.server_port,
        client_host=args.client_host,
        client_port=args.client_port,
        mdns_name=args.mdns_name,
        nymphes_osc_log_level=logging.DEBUG if args.debug_osc else logging.INFO,
        nymphes_midi_log_level=logging.DEBUG if args.debug_midi else logging.WARNING)

    #
    # Stay running until manually stopped
    #
    while True:
        nymphes_osc.update()
        time.sleep(0.0001)


if __name__ == '__main__':
    main()
