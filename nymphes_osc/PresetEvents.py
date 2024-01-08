from enum import Enum


class PresetEvents(Enum):
    recalled_preset = 'recalled_preset'
    received_current_preset_from_midi_input_port = 'received_current_preset_from_midi_input_port'

    saved_current_preset_to_file = 'saved_current_preset_to_file'
    saved_memory_slot_to_file = 'saved_memory_slot_to_file'
    loaded_file_into_current_preset = 'loaded_file_into_current_preset'
    loaded_file_into_nymphes_memory_slot = 'loaded_file_into_nymphes_memory_slot'
    loaded_default_preset = 'loaded_default_preset'

    loaded_current_preset_into_nymphes_memory_slot = 'loaded_current_preset_into_nymphes_memory_slot'

    requested_preset_dump = 'requested_preset_dump'
    received_preset_dump_from_nymphes = 'received_preset_dump_from_nymphes'
    loaded_preset_dump_from_midi_input_port_into_nymphes_memory_slot = 'loaded_preset_dump_from_midi_input_port_into_nymphes_memory_slot'

    @staticmethod
    def all_values():
        """
        Return a list of all PresetEvent values.
        :return: A list of strings
        """
        return [
            PresetEvents.recalled_preset.value,
            PresetEvents.received_current_preset_from_midi_input_port.value,

            PresetEvents.saved_current_preset_to_file.value,
            PresetEvents.saved_memory_slot_to_file.value,
            PresetEvents.loaded_file_into_current_preset.value,
            PresetEvents.loaded_file_into_nymphes_memory_slot.value,
            PresetEvents.loaded_default_preset.value,

            PresetEvents.loaded_current_preset_into_nymphes_memory_slot.value,

            PresetEvents.requested_preset_dump.value,
            PresetEvents.received_preset_dump_from_nymphes.value,
            PresetEvents.loaded_preset_dump_from_midi_input_port_into_nymphes_memory_slot.value
        ]
