import argparse
from nymphes_osc.NymphesMidiOscBridge import NymphesMidiOscBridge

def run_osc_midi_bridge(midi_port_name, 
                        midi_channel, 
                        osc_in_host, 
                        osc_in_port, 
                        osc_out_host, 
                        osc_out_port):
    
    # Create the Nymphes OSC Controller
    nymphes = NymphesMidiOscBridge(midi_port_name=midi_port_name,
                                   midi_channel=midi_channel,
                                   osc_in_host=osc_in_host,
                                   osc_in_port=osc_in_port,
                                   osc_out_host=osc_out_host,
                                   osc_out_port=osc_out_port)
    
    # Start the OSC server
    nymphes.start_osc_server()

    # Connect to the Nymphes MIDI port
    nymphes.open_nymphes_midi_port()

    # Stay running until manually killed
    while True:
        pass
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("midi_port_name", help="Name of Nymphes MIDI port, as listed using python mido library. Use double quotes if the name contains spaces.")
    parser.add_argument("midi_channel", help="MIDI channel for Nymphes synthesizer. Range: 1 to 16", 
                        type=int, default=1)
    parser.add_argument("osc_in_host", help="Host for incoming OSC messages")
    parser.add_argument("osc_in_port", help="Port used for incoming OSC messages.", type=int, default=1237)
    parser.add_argument("osc_out_host", help="Destination host for outgoing OSC messages")
    parser.add_argument("osc_out_port", help="Destination port used for outgoing OSC messages", type=int, default=1236)
    args = parser.parse_args()

    # Validate MIDI channel
    if args.midi_channel < 1 or args.midi_channel > 16:
        raise Exception(f'Invalid MIDI Channel: {args.midi_channel}. Should be between 1 and 16')

    run_osc_midi_bridge(midi_port_name=args.midi_port_name,
                        midi_channel=args.midi_channel,
                        osc_in_host=args.osc_in_host,
                        osc_in_port=args.osc_in_port,
                        osc_out_host=args.osc_out_host,
                        osc_out_port=args.osc_out_port)
