import platform
from pathlib import Path
import os


# Determine the root directory for data files (config files, logs, etc)
def get_data_files_directory_path():
    os_name = platform.system()

    if os_name == 'Darwin':
        #
        # On macOS we use ~/Library/Application Support/nymphes-osc/
        #
        return Path(os.path.expanduser('~')) / 'Library/Application Support/nymphes-osc'

    else:
        #
        # On all other systems, we use a folder in the user's home folder
        #
        return Path(os.path.expanduser('~')) / 'nymphes-osc data/'
