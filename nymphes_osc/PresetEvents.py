from enum import Enum


class PresetEvents(Enum):
    recalled_preset = 'recalled_preset'
    received_current_preset_sysex_from_midi_input_port = 'received_current_preset_sysex_from_midi_input_port'

    saved_current_preset_to_file = 'saved_current_preset_to_file'
    saved_memory_slot_to_file = 'saved_memory_slot_to_file'
    loaded_file_into_current_preset = 'loaded_file_into_current_preset'
    saved_file_to_memory_slot = 'saved_file_to_memory_slot'
    loaded_default_preset = 'loaded_default_preset'

    saved_current_preset_to_memory_slot = 'saved_current_preset_to_memory_slot'

    requested_preset_dump = 'requested_preset_dump'
    received_preset_dump_from_nymphes = 'received_preset_dump_from_nymphes'
    saved_preset_dump_from_midi_input_port_to_memory_slot = 'saved_preset_dump_from_midi_input_port_to_memory_slot'

    @staticmethod
    def all_values():
        """
        Return a list of all PresetEvent values.
        :return: A list of strings
        """
        return [
            PresetEvents.recalled_preset.value,
            PresetEvents.received_current_preset_sysex_from_midi_input_port.value,

            PresetEvents.saved_current_preset_to_file.value,
            PresetEvents.saved_memory_slot_to_file.value,
            PresetEvents.loaded_file_into_current_preset.value,
            PresetEvents.saved_file_to_memory_slot.value,
            PresetEvents.loaded_default_preset.value,

            PresetEvents.saved_current_preset_to_memory_slot.value,

            PresetEvents.requested_preset_dump.value,
            PresetEvents.received_preset_dump_from_nymphes.value,
            PresetEvents.saved_preset_dump_from_midi_input_port_to_memory_slot.value
        ]
