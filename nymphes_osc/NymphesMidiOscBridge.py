from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import mido
import mido.backends.rtmidi
from rtmidi import InvalidPortError
import time
from .OscillatorParams import OscillatorParams
from .PitchParams import PitchParams
from .AmpParams import AmpParams
from .HpfParams import HpfParams
from .Lfo1Params import Lfo1Params
from .Lfo2Params import Lfo2Params
from .LpfParams import LpfParams
from .MixParams import MixParams
from .PitchFilterEnvParams import PitchFilterEnvParams
from .ReverbParams import ReverbParams
from .ControlParameter_PlayMode import ControlParameter_PlayMode
from .ControlParameter_ModSource import ControlParameter_ModSource
from .ControlParameter_Legato import ControlParameter_Legato


class NymphesMidiOscBridge:
    """
    A class used for OSC control of all of the control parameters of the Dreadbox Nymphes synthesizer.
    We communicate with a Pure Data patch via OSC. The patch communicates with the Nymphes via MIDI.
    """

    def __init__(self, midi_channel, osc_in_host, osc_in_port, osc_out_host, osc_out_port):
        # Prepare OSC objects
        #
        self.midi_channel = midi_channel-1 # mido library is zero-referenced, so MIDI channel 1 is specified as 0
        self.in_host = osc_in_host
        self.in_port = osc_in_port
        self.out_host = osc_out_host
        self.out_port = osc_out_port

        # The OSC Server, which receives OSC messages on a background thread
        #
        self._osc_server = None
        self._osc_server_thread = None

        self._dispatcher = Dispatcher()

        # The OSC Client, which sends out OSC messages
        self._osc_client = SimpleUDPClient(osc_out_host, osc_out_port)

        # MIDI IO port for messages to and from Nymphes
        self._nymphes_midi_port = None

        # Flag indicating whether we are connected to a Nymphes synthesizer
        self.nymphes_connected = False

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

    def start_osc_server(self):
        self._osc_server = BlockingOSCUDPServer((self.in_host, self.in_port), self._dispatcher)
        self._osc_server_thread = threading.Thread(target=self._osc_server.serve_forever)
        self._osc_server_thread.start()
        
        print('nymphes_osc: Started OSC Server')
        print(f'nymphes_osc: in_host: {self.in_host}')
        print(f'nymphes_osc: in_port: {self.in_port}')
        print(f'nymphes_osc: out_host: {self.out_host}')
        print(f'nymphes_osc: out_port: {self.out_port}')

    def stop_osc_server(self):
        if self._osc_server is not None:
            self._osc_server.shutdown()
            self._osc_server.server_close()
            self._osc_server = None
            self._osc_server_thread.join()
            self._osc_server_thread = None
            print('nymphes_osc: Stopped OSC Server')

    def connect_nymphes_midi_port(self, port_name):
        """
        Opens MIDI IO port for Nymphes synthesizer
        """
        # Connect to the port
        self._nymphes_midi_port = mido.open_ioport(port_name)

        # Update connection flag
        self.nymphes_connected = True

        print(f'nymphes_osc: nymphes_osc: Opened MIDI Port {self._nymphes_midi_port.name}')
        print(f'nymphes_osc: nymphes_osc: Using MIDI channel {self.midi_channel + 1}')

    def disconnect_nymphes_midi_port(self):
        """
        Closes the MIDI IO port for the Nymphes synthesizer
        """
        if self.nymphes_connected:
            # Close the port
            self._nymphes_midi_port.close()
            print(f'nymphes_osc: nymphes_osc: Closed MIDI Port {self._nymphes_midi_port.name}')

            # We no longer need this port
            self._nymphes_midi_port = None

            # Update connection flag
            self.nymphes_connected = False

        else:
            raise Exception('No Nymphes MIDI port is connected')

    def _get_connected_nymphes_midi_port_name(self):
        """
        Checks whether there is a Dreadbox Nymphes synthesizer connected.
        Returns the name of the midi port if it is connected.
        Returns None if no Nymphes is connected.
        """

        # Return the first port name that contains the word nymphes
        for port_name in mido.get_output_names():
            if 'nymphes' in (port_name).lower():
                return port_name
            
        # If we get here, then there was no matching port
        return None

    def _detect_nymphes_connection(self):
        """
        Check whether a nymphes synthesizer is connected.
        Open a midi port when a nymphes is connected, and close
        when it disconnects.
        """
        # Check whether the Nymphes is connected
        try:
            port_name = self._get_connected_nymphes_midi_port_name()
            
            if port_name is not None:
                # A nymphes is connected
                if not self.nymphes_connected:
                    # It has just been connected. Open the port.
                    self.connect_nymphes_midi_port(port_name)
            
            else:
                # A nymphes is not connected
                if self.nymphes_connected:
                    # It has just been disconnected. Close the port.
                    self.disconnect_nymphes_midi_port()
            
        except InvalidPortError:
            print('nymphes_osc: ignoring error while attempting to get port names (rtmidi.InvalidPortError)')
                    
            
    def update(self):
        """
        Should be called regularly.
        """
        # Check for Nymphes
        self._detect_nymphes_connection()

        # Handle any incoming MIDI messages waiting for us
        if self.nymphes_connected:
            for midi_message in self._nymphes_midi_port.iter_pending():
                self.on_midi_message(midi_message)        

    def on_midi_message(self, midi_message):
        """
        To be called by the nymphes midi port when new midi messages are received
        """
        # print(f'nymphes_osc: nymphes_osc: {midi_message}')
        # Only pass on control change midi messages
        if midi_message.is_cc():

            # Only pass on messages if the channel is correct
            if midi_message.channel == self.midi_channel:
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

        # else:
        #     # A non-control change message was received.
        #     print(f'nymphes_osc: Non-Control Change Message Received: {midi_message}')

    def _nymphes_midi_send_function(self, midi_cc, value):
        """
        A function used to send a MIDI message to the Nymphes synthesizer.
        Every member object in NymphesOscController is given a reference
        to this function so it can send MIDI messages.
        """
        if self._nymphes_midi_port is not None:
            if not self._nymphes_midi_port.closed:
                # Construct the MIDI message
                msg = mido.Message('control_change', channel=self.midi_channel, control=midi_cc, value=value)

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
