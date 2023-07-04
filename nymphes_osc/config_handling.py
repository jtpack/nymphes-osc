from pathlib import Path
import configparser


def create_new_config_file(filepath):
    """
    Create a configuration file at filepath.
    If a config file already exists at filepath, 
    it will be overwritten.
    """

    config = configparser.ConfigParser()
    config['MIDI'] = {
        'port_name': 'Nymphes:Nymphes MIDI 1 20:0',
        'channel': 1
    }
    config['OSC'] = {
        'in_host': '192.168.4.73',
        'in_port': 1237,
        'out_host': '192.168.4.28',
        'out_port': 1236
    }

    # Write config file
    with open(filepath, 'w') as configfile:
        config.write(configfile)

    # Check whether the configuration file actually exists now
    if Path(filepath).exists():
        print(f'Created new configuration file with default values at {filepath}')
    else:
        raise Exception(f'Failed to create config file at {filepath}')
