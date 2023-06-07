from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
from nymphes_osc.OscillatorParams import OscillatorParams


class NymphesMidiOscBridge:
    """
    A class used for OSC control of all of the control parameters of the Dreadbox Nymphes synthesizer.
    We communicate with a Pure Data patch via OSC. The patch communicates with the Nymphes via MIDI.
    """

    def __init__(self, incoming_host, incoming_port, outgoing_host, outgoing_port, nymphes_midi_channel):
        # Prepare OSC objects
        #

        self.incoming_host = incoming_host
        self.incoming_port = incoming_port
        self.outgoing_host = outgoing_host
        self.outgoing_port = outgoing_port

        # The OSC Server, which receives incoming OSC messages on a background thread
        #

        self._osc_server = None
        self._osc_server_thread = None

        self._dispatcher = Dispatcher()

        # Start the server
        self._start_osc_server()

        # The OSC Client, which sends outgoing OSC messages
        self._osc_client = SimpleUDPClient(outgoing_host, outgoing_port)

        # The MIDI channel for the connected Nymphes synthesizer
        self.nymphes_midi_channel = nymphes_midi_channel

        # MIDI IO port for messages to and from Nymphes
        self._nymphes_midi_port = None

        # Connect the MIDI port
        self._open_nymphes_midi_port()

        # # Create the control parameter objects
        self._oscillator_params = OscillatorParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        # self._pitch_params = NymphesOscPitchParams(self.dispatcher, self._osc_send_function,
        #                                            self._nymphes_midi_send_function)
        # self._amp_params = NymphesOscAmpParams(self.dispatcher, self._osc_send_function,
        #                                        self._nymphes_midi_send_function)
        # self._mix_params = NymphesOscMixParams(self.dispatcher, self._osc_send_function,
        #                                        self._nymphes_midi_send_function)
        # self._lpf_params = NymphesOscLpfParams(self.dispatcher, self._osc_send_function,
        #                                        self._nymphes_midi_send_function)
        # self._hpf_params = NymphesOscHpfParams(self.dispatcher, self._osc_send_function,
        #                                        self._nymphes_midi_send_function)
        # self._pitch_filter_env_params = NymphesOscPitchFilterEnvParams(self.dispatcher, self._osc_send_function,
        #                                                                self._nymphes_midi_send_function)
        # self._pitch_filter_lfo_params = NymphesOscPitchFilterLfoParams(self.dispatcher, self._osc_send_function,
        #                                                                self._nymphes_midi_send_function)
        # self._lfo2_params = NymphesOscLfo2Params(self.dispatcher, self._osc_send_function,
        #                                          self._nymphes_midi_send_function)
        # self._reverb_params = NymphesOscReverbParams(self.dispatcher, self._osc_send_function,
        #                                              self._nymphes_midi_send_function)
        # self._play_mode_parameter = NymphesOscPlayModeParameter(self.dispatcher, self._osc_send_function,
        #                                                         self._nymphes_midi_send_function)
        # self._mod_source_parameter = NymphesOscModSourceParameter(self.dispatcher, self._osc_send_function,
        #                                                           self._nymphes_midi_send_function)
        # self._legato_parameter = NymphesOscLegatoParameter(self.dispatcher, self._osc_send_function,
        #                                                    self._nymphes_midi_send_function)

    def _start_osc_server(self):
        self._osc_server = BlockingOSCUDPServer((self.incoming_host, self.incoming_port), self._dispatcher)
        self._osc_server_thread = threading.Thread(target=self._osc_server.serve_forever)
        self._osc_server_thread.start()

    def _stop_osc_server(self):
        if self._osc_server is not None:
            self._osc_server.shutdown()
            self._osc_server.server_close()
            self._osc_server = None
            self._osc_server_thread.join()
            self._osc_server_thread = None

    def _open_nymphes_midi_port(self):
        """
        Opens MIDI IO port for Nymphes synthesizer
        """
        port_name = 'Nymphes Bootloader'
        self._nymphes_midi_port = mido.open_ioport(port_name, callback=self._nymphes_midi_receive_callback)

    def _close_nymphes_midi_port(self):
        """
        Closes the MIDI IO port for the Nymphes synthesizer
        """
        if self._nymphes_midi_port is not None:
            self._nymphes_midi_port.close()

    def _nymphes_midi_receive_callback(self, midi_message):
        """
        To be called by the nymphes midi port when new midi messages are received
        """
        print(midi_message)

        self._oscillator_params.on_midi_message(midi_message)


    def _nymphes_midi_send_function(self, midi_cc, value):
        """
        A function used to send a MIDI message to the Nymphes synthesizer.
        Every member object in NymphesOscController is given a reference
        to this function so it can send MIDI messages.
        """
        if self._nymphes_midi_port is not None:
            if not self._nymphes_midi_port.closed:
                # Construct the MIDI message
                msg = mido.Message('control_change', channel=self.nymphes_midi_channel, control=midi_cc, value=value)

                # Send the message
                self._nymphes_midi_port.send(msg)

    def _osc_send_function(self, osc_message):
        """
        A function used to send an OSC message.
        Every member object in NymphesOscController is given a reference
        to this function so it can send OSC messages.
        """
        self._osc_client.send(osc_message)

    @property
    def oscillator(self):
        return self._oscillator_params

    @property
    def pitch(self):
        return self._pitch_params

    @property
    def amp(self):
        return self._amp_params

    @property
    def mix(self):
        return self._mix_params

    @property
    def lpf(self):
        return self._lpf_params

    @property
    def hpf(self):
        return self._hpf_params

    @property
    def pitch_filter_env(self):
        return self._pitch_filter_env_params

    @property
    def pitch_filter_lfo(self):
        return self._pitch_filter_lfo_params

    @property
    def lfo2(self):
        return self._lfo2_params

    @property
    def reverb(self):
        return self._reverb_params

    @property
    def play_mode(self):
        return self._play_mode_parameter

    @property
    def mod_source(self):
        return self._mod_source_parameter

    @property
    def legato(self):
        return self._legato_parameter
