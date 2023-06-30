n = model.NymphesMidiOscBridge(incoming_host='192.168.4.30', incoming_port=1237, outgoing_host='juno.local', outgoing_port=1236)import subprocess


n = model.NymphesMidiOscBridge(incoming_host='192.168.4.30', incoming_port=1237, outgoing_host='juno.local', outgoing_port=1236)


def connect_alsa_midi_devices(self):
    """
    Use aconnect to connect the Nymphes and controller keyboard
    to Pd
    """
    # MIDI Input to Pd
    #

    # The Nymphes will be port 1, so its midi channels start at 1 in Pd
    subprocess.run("aconnect 'Nymphes':0 'Pure Data':0", shell=True)

    # The MicroLab will be port 2, so its midi channels start at 17 in Pd
    subprocess.run("aconnect 'Arturia MicroLab':0 'Pure Data':1", shell=True)

    # MIDI Output from Pd
    #

    # Pd will output to the Nymphes on port 1, so the MIDI channels will start at
    subprocess.run("aconnect 'Pure Data':2 'Nymphes':0", shell=True)