from nymphes_osc.ModSourceControlParameter import NymphesOscController


if __name__ == '__main__':
    incoming_host = '192.168.4.30'
    incoming_port = 1237
    outgoing_host = 'localhost'
    outgoing_port = 1236

    nymphes_midi_channel = 0

    # Create the Nymphes OSC Controller
    noc = NymphesOscController(incoming_host, incoming_port, outgoing_host, outgoing_port, nymphes_midi_channel)

    # Start the OSC server
    noc._start_osc_server()

    while True:
        pass


