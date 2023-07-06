from nymphes_osc.NymphesMidiOscBridge import NymphesMidiOscBridge
import configparser
from pathlib import Path
from nymphes_osc.config_handling import create_new_config_file

def run_osc_midi_bridge(midi_channel, 
                        osc_in_host, 
                        osc_in_port, 
                        osc_out_host, 
                        osc_out_port):
    
    # Create the Nymphes OSC Controller
    nymphes = NymphesMidiOscBridge(midi_channel=midi_channel,
                                   osc_in_host=osc_in_host,
                                   osc_in_port=osc_in_port,
                                   osc_out_host=osc_out_host,
                                   osc_out_port=osc_out_port)
    
    # Start the OSC server
    nymphes.start_osc_server()

    # Stay running until manually killed
    while True:
        nymphes.update()

if __name__ == '__main__':
    # Get configuration
    #
    config_file_path = 'config.txt'

    # Create a configuration file if one doesn't exist
    if not Path(config_file_path).exists():
        create_new_config_file(config_file_path)
    
    # Load configuration file data
    config = configparser.ConfigParser()
    config.read(config_file_path)

    midi = config['MIDI']
    osc = config['OSC']

    run_osc_midi_bridge(midi_channel=int(midi['channel']),
                        osc_in_host=osc['in_host'],
                        osc_in_port=int(osc['in_port']),
                        osc_out_host=osc['out_host'],
                        osc_out_port=int(osc['out_port']))
