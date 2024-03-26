from enum import Enum


class MidiConnectionEvents(Enum):
    nymphes_midi_input_detected = 'nymphes_midi_input_detected'
    nymphes_midi_input_no_longer_detected = 'nymphes_midi_input_no_longer_detected'

    nymphes_midi_output_detected = 'nymphes_midi_output_detected'
    nymphes_midi_output_no_longer_detected = 'nymphes_midi_output_no_longer_detected'

    nymphes_connected = 'nymphes_connected'
    nymphes_disconnected = 'nymphes_disconnected'
    
    midi_input_detected = 'midi_input_detected'
    midi_input_no_longer_detected = 'midi_input_no_longer_detected'
    midi_input_connected = 'midi_input_connected'
    midi_input_disconnected = 'midi_input_disconnected'

    midi_output_detected = 'midi_output_detected'
    midi_output_no_longer_detected = 'midi_output_no_longer_detected'
    midi_output_connected = 'midi_output_connected'
    midi_output_disconnected = 'midi_output_disconnected'

    nymphes_midi_channel_changed = 'nymphes_midi_channel_changed'

    @staticmethod
    def all_values():
        """
        Return a list of all MidiConnectionEvents values.
        :return: A list of strings
        """
        return [
            MidiConnectionEvents.nymphes_midi_input_detected.value,
            MidiConnectionEvents.nymphes_midi_input_no_longer_detected.value,

            MidiConnectionEvents.nymphes_midi_output_detected.value,
            MidiConnectionEvents.nymphes_midi_output_no_longer_detected.value,
            
            MidiConnectionEvents.nymphes_connected.value,
            MidiConnectionEvents.nymphes_disconnected.value,
            
            MidiConnectionEvents.midi_input_detected.value,
            MidiConnectionEvents.midi_input_no_longer_detected.value,
            MidiConnectionEvents.midi_input_connected.value,
            MidiConnectionEvents.midi_input_disconnected.value,

            MidiConnectionEvents.midi_output_detected.value,
            MidiConnectionEvents.midi_output_no_longer_detected.value,
            MidiConnectionEvents.midi_output_connected.value,
            MidiConnectionEvents.midi_output_disconnected.value,

            MidiConnectionEvents.nymphes_midi_channel_changed
        ]
