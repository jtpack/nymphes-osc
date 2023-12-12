from nymphes_osc.src.NymphesMidiOscBridge import NymphesMidiOscBridge
import configparser
from pathlib import Path
import time
import netifaces


def main():
    #
    # Get configuration from config file
    #
    config_file_path = 'config.txt'

    # Create a configuration file if one doesn't exist
    if not Path(config_file_path).exists():
        create_new_config_file(config_file_path)

    config = configparser.ConfigParser()
    config.read(config_file_path)

    midi = config['MIDI']
    osc = config['OSC']

    if config.has_option('OSC', 'in_host'):
        # in_host has been specified in config.txt
        in_host = osc["in_host"]
        print(f'Using in_host from {config_file_path}: {in_host}')
    else:
        # in_host is not specified.
        # We will try to automatically determine the local ip address
        in_host = get_local_ip_address()
        print(f'Using detected local ip address: {in_host}')

    #
    # Create the Nymphes OSC Controller
    #
    nymphes = NymphesMidiOscBridge(nymphes_midi_channel=int(midi['channel']), osc_in_host=in_host,
                                   osc_in_port=int(osc['in_port']))

    #
    # Stay running until manually killed
    #
    while True:
        nymphes.update()
        time.sleep(0.0001)


def create_new_config_file(filepath):
    """
    Create a configuration file at filepath.
    If a config file already exists at filepath,
    it will be overwritten.
    """

    config = configparser.ConfigParser()
    config['MIDI'] = {
        'channel': 1
    }
    config['OSC'] = {
        'in_port': 1237
    }

    # Write config file
    with open(filepath, 'w') as configfile:
        config.write(configfile)

    # Check whether the configuration file actually exists now
    if Path(filepath).exists():
        print(f'nymphes_osc: Created new configuration file with default values at {filepath}')
    else:
        raise Exception(f'Failed to create config file at {filepath}')


def get_local_ip_address():
    """
    Return the IP address of the local machine as a string.
    If no address other than 127.0.0.1 can be found, then
    return 127.0.0.1
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
        except ValueError:
            pass

    return '127.0.0.1'  # Default to localhost if no suitable IP address is found

if __name__ == '__main__':
    main()
