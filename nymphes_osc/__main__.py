import logging

from nymphes_osc.NymphesMidiOscBridge import NymphesMidiOscBridge
import time
import argparse


def main():
    #
    # Handle command-line arguments
    #

    parser = argparse.ArgumentParser()

    # Port
    # This is required
    parser.add_argument(
        '--port',
        type=int,
        default=1237,
        help='Optional. The port to use when listening for incoming OSC messages. Defaults to 1237.'
    )

    # Host
    # This is optional. If not supplied, then the local
    # IP will be detected and used
    parser.add_argument(
        '--host',
        help='Optional. The hostname or IP address to use when listening for incoming OSC messages. If not supplied, then the local IP address is detected and used'
    )

    parser.add_argument(
        '-m', '--midi_channel',
        type=int,
        default=1,
        help='Optional. MIDI Channel that Nymphes is set to use. 1 to 16. Defaults to 1.'
    )

    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Optional. Enables logging of debug messages.'
    )

    args = parser.parse_args()

    if args.debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    #
    # Create the Nymphes OSC Controller
    #
    nymphes = NymphesMidiOscBridge(
        nymphes_midi_channel=args.midi_channel,
        port=args.port,
        host=args.host,
        logging_level=logging_level
    )

    #
    # Stay running until manually killed
    #
    while True:
        nymphes.update()
        time.sleep(0.0001)


if __name__ == '__main__':
    main()
