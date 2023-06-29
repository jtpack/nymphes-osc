from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
import time
from nymphes_osc.OscillatorParams import OscillatorParams
from nymphes_osc.PitchParams import PitchParams
from nymphes_osc.AmpParams import AmpParams
from nymphes_osc.HpfParams import HpfParams
from nymphes_osc.Lfo1Params import Lfo1Params
from nymphes_osc.Lfo2Params import Lfo2Params
from nymphes_osc.LpfParams import LpfParams
from nymphes_osc.MixParams import MixParams
from nymphes_osc.PitchFilterEnvParams import PitchFilterEnvParams
from nymphes_osc.ReverbParams import ReverbParams
from nymphes_osc.ControlParameter_PlayMode import ControlParameter_PlayMode
from nymphes_osc.ControlParameter_ModSource import ControlParameter_ModSource
from nymphes_osc.ControlParameter_Legato import ControlParameter_Legato


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

        # The OSC Client, which sends outgoing OSC messages
        self._osc_client = SimpleUDPClient(outgoing_host, outgoing_port)

        # The MIDI channel for the connected Nymphes synthesizer
        self.nymphes_midi_channel = nymphes_midi_channel

        # MIDI IO port for messages to and from Nymphes
        self._nymphes_midi_port = None

        # Create the control parameter objects
        self._oscillator_params = OscillatorParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        self._pitch_params = PitchParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        self._amp_params = AmpParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        self._mix_params = MixParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        self._lpf_params = LpfParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        self._hpf_params = HpfParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        self._pitch_filter_env_params = PitchFilterEnvParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        self._lfo1_params = Lfo1Params(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        self._lfo2_params = Lfo2Params(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        self._reverb_params = ReverbParams(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        self._play_mode_parameter = ControlParameter_PlayMode(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        self._mod_source_parameter = ControlParameter_ModSource(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)
        self._legato_parameter = ControlParameter_Legato(self._dispatcher, self._osc_send_function, self._nymphes_midi_send_function)

        # Start the server
        self.start_osc_server()

        # Connect the MIDI port
        self.open_nymphes_midi_port()

    def start_osc_server(self):
        self._osc_server = BlockingOSCUDPServer((self.incoming_host, self.incoming_port), self._dispatcher)
        self._osc_server_thread = threading.Thread(target=self._osc_server.serve_forever)
        self._osc_server_thread.start()

    def stop_osc_server(self):
        if self._osc_server is not None:
            self._osc_server.shutdown()
            self._osc_server.server_close()
            self._osc_server = None
            self._osc_server_thread.join()
            self._osc_server_thread = None

    def open_nymphes_midi_port(self):
        """
        Opens MIDI IO port for Nymphes synthesizer
        """
        port_name = 'Nymphes Bootloader'
        self._nymphes_midi_port = mido.open_ioport(port_name, callback=self._on_nymphes_midi_message)

    def close_nymphes_midi_port(self):
        """
        Closes the MIDI IO port for the Nymphes synthesizer
        """
        if self._nymphes_midi_port is not None:
            self._nymphes_midi_port.close()

    def _on_nymphes_midi_message(self, midi_message):
        """
        To be called by the nymphes midi port when new midi messages are received
        """
        # Only pass on control change midi messages
        if midi_message.is_cc():

            # Only pass on messages if the channel is correct
            if midi_message.channel == self.nymphes_midi_channel:
                self.amp.on_midi_message(midi_message)
                self.hpf.on_midi_message(midi_message)
                self.lfo1.on_midi_message(midi_message)
                self.lfo2.on_midi_message(midi_message)
                self.lpf.on_midi_message(midi_message)
                self.mix.on_midi_message(midi_message)
                self.oscillator.on_midi_message(midi_message)
                self.pitch_filter_env.on_midi_message(midi_message)
                self.pitch.on_midi_message(midi_message)
                self.reverb.on_midi_message(midi_message)
                self.play_mode.on_midi_message(midi_message)
                self.mod_source.on_midi_message(midi_message)
                self.legato.on_midi_message(midi_message)

        else:
            # A non-control change message was received.
            print(f'Non-Control Change Message Received: {midi_message}')

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
    def lfo1(self):
        return self._lfo1_params

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
