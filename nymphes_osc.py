from nymphes_osc.NymphesMidiOscBridge import NymphesMidiOscBridge


if __name__ == '__main__':

    # Create the Nymphes OSC Controller
    nymphes = NymphesMidiOscBridge(incoming_host='localhost',
                               incoming_port=1237,
                               outgoing_host='localhost',
                               outgoing_port=1236,
                               nymphes_midi_channel=0)

    # Start the OSC server
    #nymphes.start_osc_server()

    # Open the MIDI port
    #nymphes.open_nymphes_midi_port()

    while True:
        pass


