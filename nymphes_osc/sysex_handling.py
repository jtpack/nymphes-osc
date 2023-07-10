import preset_pb2

def preset_from_sysex_data(sysex_data):
    """
    Extracts Nymphes preset data from the supplied MIDI sysex data.
    sysex_data should be a list of bytes.
    """

    # Make sure this really is a Dreadbox Nymphes sysex message
    #

    # Check for Dreadbox manufacturer id
    if not (sysex_data[0] == 0x00 and sysex_data[1] == 0x21 and sysex_data[2] == 0x35):
        print('This sysex message does not have the id for Dreadbox')
        return None
    
    # Check for Nymphes model id
    if sysex_data[4] != 0x06:
        print('This sysex message is Dreadbox, but the device id is not Nymphes')
        return None
    
    print('This is a Dreadbox Nymphes sysex message')

    # Check the type of preset import
    if sysex_data[5] == 0x00:
        print('Non-persistent preset load')
    elif sysex_data[5] == 0x01:
        print('Persistent preset import')

    # Determine user or factory preset type
    if sysex_data[6] == 0x00:
        print('User preset')
    elif sysex_data[6] == 0x01:
        print('Factory preset')
    
    # Get bank and preset
    # Note: Both start at 1, not zero
    bank = sysex_data[7]
    preset_number = sysex_data[8]
    print(f'Bank {bank}, preset {preset_number}')

    # Get CRC
    crc_lsb_nibble = sysex_data[9]
    crc_msb_nibble = sysex_data[10]

    # Get "nibblized" protobuf sysex data
    sysex_data = sysex_data[11:]
    
    # hex_data = [hex(val) for val in nibblized_protobuf_sysex_data]
    # print(hex_data)

    # Get just the protobuf data
    protobuf_data = extract_nibblized_protobuf_message(sysex_data)

    print(f'F8 index: {protobuf_data.index(0xF8)}')


    # Attempt to interpret the sysex message
    # data_bytes = bytes(protobuf_data)
    # p = preset()
    # p.ParseFromString(data_bytes)
    # print(p)

def calculate_crc8(data):
    crc_table = [
        0x00, 0x31, 0x62, 0x53, 0xc4, 0xf5, 0xa6, 0x97, 0xb9, 0x88, 0xdb, 0xea, 0x7d,
        0x4c, 0x1f, 0x2e, 0x43, 0x72, 0x21, 0x10, 0x87, 0xb6, 0xe5, 0xd4, 0xfa, 0xcb,
        0x98, 0xa9, 0x3e, 0x0f, 0x5c, 0x6d, 0x86, 0xb7, 0xe4, 0xd5, 0x42, 0x73, 0x20,
        0x11, 0x3f, 0x0e, 0x5d, 0x6c, 0xfb, 0xca, 0x99, 0xa8, 0xc5, 0xf4, 0xa7, 0x96,
        0x01, 0x30, 0x63, 0x52, 0x7c, 0x4d, 0x1e, 0x2f, 0xb8, 0x89, 0xda, 0xeb, 0x3d,
        0x0c, 0x5f, 0x6e, 0xf9, 0xc8, 0x9b, 0xaa, 0x84, 0xb5, 0xe6, 0xd7, 0x40, 0x71,
        0x22, 0x13, 0x7e, 0x4f, 0x1c, 0x2d, 0xba, 0x8b, 0xd8, 0xe9, 0xc7, 0xf6, 0xa5,
        0x94, 0x03, 0x32, 0x61, 0x50, 0xbb, 0x8a, 0xd9, 0xe8, 0x7f, 0x4e, 0x1d, 0x2c,
        0x02, 0x33, 0x60, 0x51, 0xc6, 0xf7, 0xa4, 0x95, 0xf8, 0xc9, 0x9a, 0xab, 0x3c,
        0x0d, 0x5e, 0x6f, 0x41, 0x70, 0x23, 0x12, 0x85, 0xb4, 0xe7, 0xd6, 0x7a, 0x4b,
        0x18, 0x29, 0xbe, 0x8f, 0xdc, 0xed, 0xc3, 0xf2, 0xa1, 0x90, 0x07, 0x36, 0x65,
        0x54, 0x39, 0x08, 0x5b, 0x6a, 0xfd, 0xcc, 0x9f, 0xae, 0x80, 0xb1, 0xe2, 0xd3,
        0x44, 0x75, 0x26, 0x17, 0xfc, 0xcd, 0x9e, 0xaf, 0x38, 0x09, 0x5a, 0x6b, 0x45,
        0x74, 0x27, 0x16, 0x81, 0xb0, 0xe3, 0xd2, 0xbf, 0x8e, 0xdd, 0xec, 0x7b, 0x4a,
        0x19, 0x28, 0x06, 0x37, 0x64, 0x55, 0xc2, 0xf3, 0xa0, 0x91, 0x47, 0x76, 0x25,
        0x14, 0x83, 0xb2, 0xe1, 0xd0, 0xfe, 0xcf, 0x9c, 0xad, 0x3a, 0x0b, 0x58, 0x69,
        0x04, 0x35, 0x66, 0x57, 0xc0, 0xf1, 0xa2, 0x93, 0xbd, 0x8c, 0xdf, 0xee, 0x79,
        0x48, 0x1b, 0x2a, 0xc1, 0xf0, 0xa3, 0x92, 0x05, 0x34, 0x67, 0x56, 0x78, 0x49,
        0x1a, 0x2b, 0xbc, 0x8d, 0xde, 0xef, 0x82, 0xb3, 0xe0, 0xd1, 0x46, 0x77, 0x24,
        0x15, 0x3b, 0x0a, 0x59, 0x68, 0xff, 0xce, 0x9d, 0xac
    ]

    crc = 0x00
    for byte in data:
        crc = crc_table[crc ^ byte]
    return crc

def extract_nibblized_protobuf_message(sysex_data):
    # Extract the nibblized protobuf message from the SysEx message
    # The exact logic for extracting the nibblized protobuf message depends on your specific MIDI protocol and format
    # You'll need to implement the extraction logic here based on the provided information about the SysEx format
    # This function should return the nibblized protobuf message as a string
    nibblized_protobuf_message = []

    # Extract the nibblized protobuf message
    for i in range(0, len(sysex_data), 2):
        nibble1 = sysex_data[i]
        nibble2 = sysex_data[i+1]
        nibblized_protobuf_message.append(nibble1 + nibble2)

    return nibblized_protobuf_message

def create_default_preset():
    # Create a new preset message
    preset = preset_pb2.preset()

    # Set all required parameters to 0
    preset.main.wave = 0
    preset.main.lvl = 0
    preset.main.sub = 0
    preset.main.noise = 0
    preset.main.osc_lfo = 0
    preset.main.cut = 0
    preset.main.reson = 0
    preset.main.cut_eg = 0
    preset.main.a1 = 0
    preset.main.d1 = 0
    preset.main.s1 = 0
    preset.main.r1 = 0
    preset.main.lfo_rate = 0
    preset.main.lfo_wave = 0
    preset.main.pw = 0
    preset.main.glide = 0
    preset.main.dtune = 0
    preset.main.chord = 0
    preset.main.osc_eg = 0
    preset.main.hpf = 0
    preset.main.track = 0
    preset.main.cut_lfo = 0
    preset.main.a2 = 0
    preset.main.d2 = 0
    preset.main.s2 = 0
    preset.main.r2 = 0
    preset.main.lfo_delay = 0
    preset.main.lfo_fade = 0

    preset.reverb.size = 0
    preset.reverb.decay = 0
    preset.reverb.filter = 0
    preset.reverb.mix = 0

    # preset.lfo_2.lfo_1_speed_mode = preset_pb2.lfo_speed_mode.slow
    # preset.lfo_2.lfo_1_sync_mode = preset_pb2.lfo_sync_mode.free
    # preset.lfo_2.lfo_2_speed_mode = preset_pb2.lfo_speed_mode.slow
    # preset.lfo_2.lfo_2_sync_mode = preset_pb2.lfo_sync_mode.free

    preset.legato = False

    preset.voice_mode = preset_pb2.voice_mode.poly

    preset.chord_1.root = 0
    preset.chord_1.semi_1 = 0
    preset.chord_1.semi_2 = 0
    preset.chord_1.semi_3 = 0
    preset.chord_1.semi_4 = 0
    preset.chord_1.semi_5 = 0

    preset.extra_lfo_2.lfo_1_rate = 0
    preset.extra_lfo_2.lfo_1_wave = 0
    preset.extra_lfo_2.lfo_1_delay = 0
    preset.extra_lfo_2.lfo_1_fade = 0
    preset.extra_lfo_2.lfo_2_rate = 0
    preset.extra_lfo_2.lfo_2_wave = 0
    preset.extra_lfo_2.lfo_2_delay = 0
    preset.extra_lfo_2.lfo_2_fade = 0

    preset.extra_mod_w.lfo_2_rate = 0
    preset.extra_mod_w.lfo_2_wave = 0
    preset.extra_mod_w.lfo_2_delay = 0
    preset.extra_mod_w.lfo_2_fade = 0

    preset.extra_velo.lfo_2_rate = 0
    preset.extra_velo.lfo_2_wave = 0
    preset.extra_velo.lfo_2_delay = 0
    preset.extra_velo.lfo_2_fade = 0

    preset.extra_after.lfo_2_rate = 0
    preset.extra_after.lfo_2_wave = 0
    preset.extra_after.lfo_2_delay = 0
    preset.extra_after.lfo_2_fade = 0

    preset.amp_level = 0

    preset.lfo_2.CopyFrom(preset_pb2.basic_inputs())
    preset.mod_w.CopyFrom(preset_pb2.extra_modulation_parameters())
    preset.velo.CopyFrom(preset_pb2.extra_modulation_parameters())
    preset.after.CopyFrom(preset_pb2.extra_modulation_parameters())
    preset.lfo_settings.lfo_1_speed_mode = preset_pb2.lfo_speed_mode.slow
    preset.lfo_settings.lfo_1_sync_mode = preset_pb2.lfo_sync_mode.free
    preset.lfo_settings.lfo_2_speed_mode = preset_pb2.lfo_speed_mode.slow
    preset.lfo_settings.lfo_2_sync_mode = preset_pb2.lfo_sync_mode.free
    preset.chord_2.CopyFrom(preset_pb2.chord_info())
    preset.chord_3.CopyFrom(preset_pb2.chord_info())
    preset.chord_4.CopyFrom(preset_pb2.chord_info())
    preset.chord_5.CopyFrom(preset_pb2.chord_info())
    preset.chord_6.CopyFrom(preset_pb2.chord_info())
    preset.chord_7.CopyFrom(preset_pb2.chord_info())
    preset.chord_8.CopyFrom(preset_pb2.chord_info())

    return preset

# # Create a default preset
# default_preset = create_default_preset()

# # Print the default preset
# print(default_preset)

# # Convert to bytes
# p_bytes = default_preset.SerializeToString()
# print(p_bytes)
