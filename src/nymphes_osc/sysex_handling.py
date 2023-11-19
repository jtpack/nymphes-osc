import preset_pb2
from pathlib import Path
from google.protobuf import text_format
import netifaces


def preset_from_sysex_data(sysex_data):
    """
    Extracts Nymphes preset data from the supplied MIDI sysex data.
    sysex_data should be a list of bytes.
    Returns a tuple: (preset_object, preset_import_type, user_or_factory, bank_number, preset_number)
    """

    # Verify Dreadbox Manufacturer ID
    if not (sysex_data[0] == 0x00 and sysex_data[1] == 0x21 and sysex_data[2] == 0x35):
        print('This sysex message does not have the id for Dreadbox')
        return None

    # Skip byte 3 - device ID, as it is not used

    # Verify Nymphes Model ID
    if sysex_data[4] != 0x06:
        print('This sysex message is Dreadbox, but the device id is not Nymphes')
        return None

    # Preset data starts at byte 11. It has been encoded using the protobuf
    # system, and then "nibblized" - each protobuf byte has been transmitted
    # as a pair of bytes because midi sysex only uses 7 bits of each byte.
    nibblized_protobuf_data = sysex_data[11:]

    # Un-nibblize the data - combine the nibbles to convert back to 8-bit bytes
    protobuf_data = bytes_from_nibbles(nibblized_protobuf_data)

    # Verify CRC to make sure the data has not been corrupted
    #

    # Get the CRC check value, which also was nibblized
    sysex_crc_ls_nibble = sysex_data[9]
    sysex_crc_ms_nibble = sysex_data[10]

    # Calculate CRC from protobuf data
    crc = calculate_crc8(protobuf_data)

    # Convert to nibbles
    protobuf_crc_ms_nibble, protobuf_crc_ls_nibble = nibble_from_byte(crc)

    # Make sure the calculated CRC matches the transmitted CRC value
    if protobuf_crc_ms_nibble != sysex_crc_ms_nibble or protobuf_crc_ls_nibble != sysex_crc_ls_nibble:
        raise Exception(
            f'CRC failed: (sysex {sysex_crc_ms_nibble}:{sysex_crc_ls_nibble}, calculated from protobuf: {protobuf_crc_ms_nibble}, {protobuf_crc_ls_nibble})')

    # Convert protobuf data to a preset
    p = preset_pb2.preset.FromString(bytes(protobuf_data))

    # Get the preset import type
    preset_import_type = 'persistent' if sysex_data[5] == 0x01 else 'non-persistent'

    # Determine user or factory preset type
    preset_type = 'user' if sysex_data[6] == 0 else 'factory'

    # Get bank name. We will return it as a capital letter from A to G
    bank_name = ['A', 'B', 'C', 'D', 'E', 'F', 'G'][sysex_data[7]-1]

    # Get preset number. It is a number between 1 and 7
    preset_number = sysex_data[8]

    return p, preset_import_type, preset_type, bank_name, preset_number


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

def bytes_from_nibbles(nibbles):
    bytes_list = []

    for i in range(0, len(nibbles), 2):

        # The first byte in the nibble is the LSB
        nibble1 = nibbles[i]

        # The second byte in the nibble is the MSB,
        # so shift it by 4 bits
        nibble2 = nibbles[i + 1] << 4

        bytes_list.append(nibble1 + nibble2)

    return bytes_list

def nibbles_from_bytes(bytes):
    sysex_data = []

    for byte in bytes:
        ms, ls = nibble_from_byte(byte)
        sysex_data.append(ls)
        sysex_data.append(ms)

    return sysex_data

def nibble_from_byte(byte):
    """
    Breaks byte into its most significant 4 bits and least significant 4 bits,
    and returns their values as a tuple of integers.
    Index 0 is the most significant value
    Index 1 is the least significant
    """
    # Shift the entire value right by 4 bits
    ms = byte >> 4

    # Use a bitwise AND to mask out the most significant
    # 4 bits, so only the least significant remain
    ls = byte & 0b00001111

    return ms, ls


def print_nymphes_preset(nymphes_preset):
    """
    Print all parameters of a Nymphes sysex preset
    """
    pass

def create_default_preset():
    # Create a new preset message
    p = preset_pb2.preset()

    # Parameter Values
    p.main.wave = 0.0
    p.main.lvl = 0.0
    p.main.sub = 0.0
    p.main.noise = 0.0
    p.main.osc_lfo = 0.0
    p.main.cut = 0.0
    p.main.reson = 0.0
    p.main.cut_eg = 0.0
    p.main.a1 = 0.0
    p.main.d1 = 0.0
    p.main.s1 = 0.0
    p.main.r1 = 0.0
    p.main.lfo_rate = 0.0
    p.main.lfo_wave = 0.0
    p.main.pw = 0.0
    p.main.glide = 0.0
    p.main.dtune = 0.0
    p.main.chord = 0.0
    p.main.osc_eg = 0.0
    p.main.hpf = 0.0
    p.main.track = 0.0
    p.main.cut_lfo = 0.0
    p.main.a2 = 0.0
    p.main.d2 = 0.0
    p.main.s2 = 0.0
    p.main.r2 = 0.0
    p.main.lfo_delay = 0.0
    p.main.lfo_fade = 0.0

    p.reverb.size = 0.0
    p.reverb.decay = 0.0
    p.reverb.filter = 0.0
    p.reverb.mix = 0.0

    # Modulation Matrix Values
    #

    # LFO2
    p.lfo_2.wave = 0.0
    p.lfo_2.lvl = 0.0
    p.lfo_2.sub = 0.0
    p.lfo_2.noise = 0.0
    p.lfo_2.osc_lfo = 0.0
    p.lfo_2.cut = 0.0
    p.lfo_2.reson = 0.0
    p.lfo_2.cut_eg = 0.0
    p.lfo_2.a1 = 0.0
    p.lfo_2.d1 = 0.0
    p.lfo_2.s1 = 0.0
    p.lfo_2.r1 = 0.0
    p.lfo_2.lfo_rate = 0.0
    p.lfo_2.lfo_wave = 0.0
    p.lfo_2.pw = 0.0
    p.lfo_2.glide = 0.0
    p.lfo_2.dtune = 0.0
    p.lfo_2.chord = 0.0
    p.lfo_2.osc_eg = 0.0
    p.lfo_2.hpf = 0.0
    p.lfo_2.track = 0.0
    p.lfo_2.cut_lfo = 0.0
    p.lfo_2.a2 = 0.0
    p.lfo_2.d2 = 0.0
    p.lfo_2.s2 = 0.0
    p.lfo_2.r2 = 0.0
    p.lfo_2.lfo_delay = 0.0
    p.lfo_2.lfo_fade = 0.0
    
    # Mod Wheel
    p.mod_w.wave = 0.0
    p.mod_w.lvl = 0.0
    p.mod_w.sub = 0.0
    p.mod_w.noise = 0.0
    p.mod_w.osc_lfo = 0.0
    p.mod_w.cut = 0.0
    p.mod_w.reson = 0.0
    p.mod_w.cut_eg = 0.0
    p.mod_w.a1 = 0.0
    p.mod_w.d1 = 0.0
    p.mod_w.s1 = 0.0
    p.mod_w.r1 = 0.0
    p.mod_w.lfo_rate = 0.0
    p.mod_w.lfo_wave = 0.0
    p.mod_w.pw = 0.0
    p.mod_w.glide = 0.0
    p.mod_w.dtune = 0.0
    p.mod_w.chord = 0.0
    p.mod_w.osc_eg = 0.0
    p.mod_w.hpf = 0.0
    p.mod_w.track = 0.0
    p.mod_w.cut_lfo = 0.0
    p.mod_w.a2 = 0.0
    p.mod_w.d2 = 0.0
    p.mod_w.s2 = 0.0
    p.mod_w.r2 = 0.0
    p.mod_w.lfo_delay = 0.0
    p.mod_w.lfo_fade = 0.0

    # Velocity
    p.velo.wave = 0.0
    p.velo.lvl = 0.0
    p.velo.sub = 0.0
    p.velo.noise = 0.0
    p.velo.osc_lfo = 0.0
    p.velo.cut = 0.0
    p.velo.reson = 0.0
    p.velo.cut_eg = 0.0
    p.velo.a1 = 0.0
    p.velo.d1 = 0.0
    p.velo.s1 = 0.0
    p.velo.r1 = 0.0
    p.velo.lfo_rate = 0.0
    p.velo.lfo_wave = 0.0
    p.velo.pw = 0.0
    p.velo.glide = 0.0
    p.velo.dtune = 0.0
    p.velo.chord = 0.0
    p.velo.osc_eg = 0.0
    p.velo.hpf = 0.0
    p.velo.track = 0.0
    p.velo.cut_lfo = 0.0
    p.velo.a2 = 0.0
    p.velo.d2 = 0.0
    p.velo.s2 = 0.0
    p.velo.r2 = 0.0
    p.velo.lfo_delay = 0.0
    p.velo.lfo_fade = 0.0
    
    # Aftertouch
    p.after.wave = 0.0
    p.after.lvl = 0.0
    p.after.sub = 0.0
    p.after.noise = 0.0
    p.after.osc_lfo = 0.0
    p.after.cut = 0.0
    p.after.reson = 0.0
    p.after.cut_eg = 0.0
    p.after.a1 = 0.0
    p.after.d1 = 0.0
    p.after.s1 = 0.0
    p.after.r1 = 0.0
    p.after.lfo_rate = 0.0
    p.after.lfo_wave = 0.0
    p.after.pw = 0.0
    p.after.glide = 0.0
    p.after.dtune = 0.0
    p.after.chord = 0.0
    p.after.osc_eg = 0.0
    p.after.hpf = 0.0
    p.after.track = 0.0
    p.after.cut_lfo = 0.0
    p.after.a2 = 0.0
    p.after.d2 = 0.0
    p.after.s2 = 0.0
    p.after.r2 = 0.0
    p.after.lfo_delay = 0.0
    p.after.lfo_fade = 0.0
    
    # LFO Settings
    p.lfo_settings.lfo_1_speed_mode = preset_pb2.lfo_speed_mode.slow
    p.lfo_settings.lfo_1_sync_mode = preset_pb2.lfo_sync_mode.free
    p.lfo_settings.lfo_2_speed_mode = preset_pb2.lfo_speed_mode.slow
    p.lfo_settings.lfo_2_sync_mode = preset_pb2.lfo_sync_mode.free

    # Legato
    p.legato = False

    # Voice Mode
    p.voice_mode = preset_pb2.voice_mode.poly

    # Chord Settings
    p.chord_1.root = 0
    p.chord_1.semi_1 = 0
    p.chord_1.semi_2 = 0
    p.chord_1.semi_3 = 0
    p.chord_1.semi_4 = 0
    p.chord_1.semi_5 = 0

    p.chord_2.root = 0
    p.chord_2.semi_1 = 0
    p.chord_2.semi_2 = 0
    p.chord_2.semi_3 = 0
    p.chord_2.semi_4 = 0
    p.chord_2.semi_5 = 0

    p.chord_3.root = 0
    p.chord_3.semi_1 = 0
    p.chord_3.semi_2 = 0
    p.chord_3.semi_3 = 0
    p.chord_3.semi_4 = 0
    p.chord_3.semi_5 = 0

    p.chord_4.root = 0
    p.chord_4.semi_1 = 0
    p.chord_4.semi_2 = 0
    p.chord_4.semi_3 = 0
    p.chord_4.semi_4 = 0
    p.chord_4.semi_5 = 0

    p.chord_5.root = 0
    p.chord_5.semi_1 = 0
    p.chord_5.semi_2 = 0
    p.chord_5.semi_3 = 0
    p.chord_5.semi_4 = 0
    p.chord_5.semi_5 = 0

    p.chord_6.root = 0
    p.chord_6.semi_1 = 0
    p.chord_6.semi_2 = 0
    p.chord_6.semi_3 = 0
    p.chord_6.semi_4 = 0
    p.chord_6.semi_5 = 0

    p.chord_7.root = 0
    p.chord_7.semi_1 = 0
    p.chord_7.semi_2 = 0
    p.chord_7.semi_3 = 0
    p.chord_7.semi_4 = 0
    p.chord_7.semi_5 = 0

    p.chord_8.root = 0
    p.chord_8.semi_1 = 0
    p.chord_8.semi_2 = 0
    p.chord_8.semi_3 = 0
    p.chord_8.semi_4 = 0
    p.chord_8.semi_5 = 0
    
    # Extra LFO Parameters
    p.extra_lfo_2.lfo_1_rate = 0.0
    p.extra_lfo_2.lfo_1_wave = 0.0
    p.extra_lfo_2.lfo_1_delay = 0.0
    p.extra_lfo_2.lfo_1_fade = 0.0
    
    p.extra_lfo_2.lfo_2_rate = 0.0
    p.extra_lfo_2.lfo_2_wave = 0.0
    p.extra_lfo_2.lfo_2_delay = 0.0
    p.extra_lfo_2.lfo_2_fade = 0.0
    
    # "Extra Modulation Parameters",
    # ie: Modulation Matrix Targeting LFO2
    p.extra_mod_w.lfo_2_rate = 0.0
    p.extra_mod_w.lfo_2_wave = 0.0
    p.extra_mod_w.lfo_2_delay = 0.0
    p.extra_mod_w.lfo_2_fade = 0.0

    p.extra_velo.lfo_2_rate = 0.0
    p.extra_velo.lfo_2_wave = 0.0
    p.extra_velo.lfo_2_delay = 0.0
    p.extra_velo.lfo_2_fade = 0.0

    p.extra_after.lfo_2_rate = 0.0
    p.extra_after.lfo_2_wave = 0.0
    p.extra_after.lfo_2_delay = 0.0
    p.extra_after.lfo_2_fade = 0.0

    p.amp_level = 0.0

    return p

def save_preset_file(preset_object, file_path):
    """
    Store a human-readable string representation of preset_object to a text
    file at file_path
    preset_object should be a valid preset_pb2.preset object
    file_path is a Path or a string
    """

    # Validate preset_object
    if not isinstance(preset_object, preset_pb2.preset):
        raise Exception(f'Invalid preset_object ({preset_object})')

    # Validate file_path
    #
    if isinstance(file_path, str):
        # Create a Path from file_path
        file_path = Path(file_path)

    if not isinstance(file_path, Path):
        raise Exception(f'file_path is neither a Path nor a string ({file_path})')

    # Write to the file
    with open(file_path, 'w') as file:
        file.write(str(preset_object))

def load_preset_file(file_path):
    """
    Reads human-readable string representation of a preset from a text file
    at file_path, and returns a preset_pb2.preset object.
    file_path is a Path or a string
    """

    # Validate file_path
    #
    if isinstance(file_path, str):
        # Create a Path from file_path
        file_path = Path(file_path)

    if not isinstance(file_path, Path):
        raise Exception(f'file_path is neither a Path nor a string ({file_path})')

    # Read from the file
    with open(file_path, 'r') as file:
        file_text = file.read()

    # Convert into a preset object
    p = preset_pb2.preset()
    text_format.Parse(file_text, p)
    return p

def sysex_data_from_preset_object(preset_object, preset_import_type, user_or_factory, bank_number, preset_number):
    """
    Generates sysex data that can be used to create a sysex MIDI message to send a preset
    to the Nymphes.
    Arguments:
        preset_object: a preset_pb2.preset object
        preset_import_type (int) 0: non persistent preset load, 1: persistent preset import
        user_or_factory (int) 0: user preset, 1: factory preset
        bank_number (int): 1 to 7
        preset_number (int): 1 to 7

    Returns: A list of bytes
    """
    # Validate arguments
    #
    if preset_object is None or not isinstance(preset_object, preset_pb2.preset):
        raise Exception(f'preset_object invalid: {preset_object}')

    if preset_import_type not in [0, 1]:
        raise Exception(f'preset_import_type invalid (should be 0 or 1): {preset_import_type}')

    if user_or_factory not in [0, 1]:
        raise Exception(f'user_or_factory invalid (should be 0 or 1): {user_or_factory}')

    if bank_number not in [1, 2, 3, 4, 5, 6, 7]:
        raise Exception(f'bank_number invalid (should be 1-7): {bank_number}')
    
    if preset_number not in [1, 2, 3, 4, 5, 6, 7]:
        raise Exception(f'preset_number invalid (should be 1-7): {preset_number}')

    sysex_data = []

    # Dreadbox ID
    sysex_data.extend([0x00, 0x21, 0x35])

    # Device ID (unused)
    sysex_data.append(0x00)

    # Model ID - Nymphes
    sysex_data.append(0x06)

    # Preset Import Type
    # 0: Non-persistent preset load
    # 1: Persistent preset import
    sysex_data.append(preset_import_type)

    # User or Factory Preset Type
    # 0: User
    # 1: Factory
    sysex_data.append(user_or_factory)

    # Bank Number
    sysex_data.append(bank_number)

    # Preset Number
    sysex_data.append(preset_number)

    # Serialize the preset_object to a list of protobuf bytes
    protobuf_data = list(preset_object.SerializeToString())

    # CRC
    #
    # Calculate CRC from the protobuf bytes
    crc_byte = calculate_crc8(protobuf_data)

    # Get nibble from the CRC
    crc_ms, crc_ls = nibble_from_byte(crc_byte)

    sysex_data.extend([crc_ls, crc_ms])

    # Get nibblized version of protobuf_data
    protobuf_nibbles = nibbles_from_bytes(protobuf_data)

    sysex_data.extend(protobuf_nibbles)

    return sysex_data

def get_local_ip_address():
    """
    Return the IP address of the local machine as a string.
    If no address other than 127.0.0.1 can be found, then
    return 127.0.0.1
    """
    # Get a list of all network interfaces
    interfaces = netifaces.interfaces()

    for iface in interfaces:
        try:
            # Get the addresses associated with the interface
            addresses = netifaces.ifaddresses(iface)

            # Extract the IPv4 addresses (if available)
            if netifaces.AF_INET in addresses:
                ip_info = addresses[netifaces.AF_INET][0]
                ip_address = ip_info['addr']
                if ip_address != '127.0.0.1':
                    return ip_address
        except ValueError:
            pass

    return '127.0.0.1'  # Default to localhost if no suitable IP address is found
