# nymphes-osc

### A command-line application which provides full control of the Dreadbox Nymphes synthesizer, via OSC (Open Sound Control) messages.
### Written in python

# Why did I make this?
I have a Dreadbox Nymphes synthesizer, and I love it. Its huge and real sound continues to surprise and delight me even after owning it for a couple of years. The modulation matrix is immense, and every time I play with it I'm impressed with what I hear.

Early experiments with MIDI controlling the Nymphes led to this project. 
- I wanted a way to view all of Nymphes' parameters when I recall a preset, including the modulation matrix and chord settings. I felt that if I could really dig into the details of a preset, amazing things might happen. 
- I wanted to be able to load and save presets as files, and to be able to share them. 
- I also wanted a way to easily pass messages from USB MIDI controllers to Nymphes. 
- Along the way, I learned that most parameters are controllable using greater than 0-127 integer resolution using SYSEX, so I also wanted to be able to take advantage of this. 

# What is nymphes-osc?
nymphes-osc is a command-line application. It detects and manages a USB MIDI connection with the Nymphes synthesizer and handles all of the complexity of using the right kinds of MIDI messages for each parameter, and it acts as an OSC server, allowing clients to send and receive OSC messages to control the Nymphes and be informed of all of its parameters.

# Why OSC?
- OSC is a well-established standard at this point, and many powerful tools exist
   - You can use an app like TouchOSC to create your own custom GUI with no coding required.
   - If you want to go lower-level, it is (relatively) easy to write a python application that speaks OSC and provides a completely custom GUI that fits your needs exactly.
- OSC is network-based, so messages can be exchanged by devices anywhere on the network. Here are a few possibilities:
   - Connect Nymphes and your USB MIDI controllers to a Raspberry Pi running nymphes-osc. Control it from an iPad running TouchOSC
   - Use a touchscreen with the Raspberry Pi
   - Run everything on a laptop, alongside a DAW and other music applications
   - Build a microcontroller-based physical controller which communicates via OSC with nymphes-osc

# What platforms are supported?
- macOS
- Linux
   - Including Raspberry Pi OS

We hope to be able to support Windows in the future.

# Projects Which Use nymphes-osc:
Coming soon...
[Blue and Pink Synth Editor](https://github.com/jtpack/Blue-and-Pink-Synth-Editor)

# How to Get Started:

## 1. Clone this repository to your home directory
   - `cd ~`
   - `git clone https://github.com/jtpack/nymphes-osc.git`

## 2. Create a virtual environment and activate it
- `cd nymphes-osc`
- `python3 -m venv venv`
- `source venv/bin/activate`

## 3. Install the nymphes-osc package into the virtual environment
`pip install -e .`

## 4. Run nymphes-osc
`python run.py`

## 5. Build an executable
- `pyinstaller nymphes-osc.spec`
  - The executable file will be in the dist folder:
    - ie: nymphes-osc/dist/nymphes-osc

# Using nymphes-osc:
- Run it on the command line and send it OSC messages.
  - `nymphes-osc`
- Register as an OSC client to receive OSC messages from nymphes-osc.
- Write a program which runs nymphes-osc in the background

# Command Line Arguments
`--server_host "SERVER_HOST"`
  - The hostname or IP address to use when listening for incoming OSC messages.
  - Type: String. Use quotes around the host name or IP address.
  - Optional. If not supplied, then the local IP address is detected and used

`--server_port SERVER_PORT`
  - The port to use when listening for incoming OSC messages.
  - Type: Int
  - Optional. If not supplied, use 1237.
  
`--client_host "CLIENT_HOST"`
  - The hostname or IP address to use for the OSC client.
  - Type: String. Use quotes around the host name or IP address.
  - Optional. If not supplied, then the server will wait for clients to register themselves.

`--client_port CLIENT_PORT`
  - The port to use for the OSC client. 
  - Type: Int
  - Optional. If not supplied, then the server will wait for clients to register themselves.

`--midi_channel MIDI_CHANNEL`
  - The MIDI Channel that Nymphes is set to use. 1 to 16.
  - Type: Int
  - Optional. If not supplied, then 1 is used.

`--use_mdns`
  - If supplied, then use mDNS to advertise on the network
  - Type: Flag.
  - Optional. If not supplied, then mDNS will not be used.

`--custom_mdns_name "MDNS_NAME"`
  - If supplied, and if --use_mdns is also supplied, then use mDNS to advertise on the network with this name
  - Type: String. Use quotes around the name.
  - Optional. If not supplied, then 

`--osc_log_level LOG_LEVEL`
  - Sets the log level for nymphes_osc
  - Type: String. Possible values: critical, warning, debug, error, info
  - Optional. If not supplied, then info is used.

`--midi_log_level LOG_LEVEL`
  - Sets the log level for nymphes_midi
  - Type: String. Possible values: critical, warning, debug, error, info
  - Optional. If not supplied, then info is used.

`--presets_directory_path "PATH"`
  - The path to use for preset files
  - Type: String. Use quotes around the path.
  - Optional. If not supplied, then use ~/nymphes_presets

You can also use `nymphes-osc --help` to see a help message listing the arguments

# Features


# OSC Commands Reference

## OSC Client Registration

#### /register_client
- Description: Register an OSC client specifying the port. The sender's IP address will be detected and used as the client's IP address.
- Arguments:
  - 0
    - Type: Int
    - Description: Port that host will be listening on

#### /register_client_with_ip_address
- Description: Register an OSC client, specifying the IP address and port.
- Arguments:
  - 0
    - Type: String
    - Description: Host name or IP address (ie: 192.168.0.52)
  - 1
    - Type: Int
    - Description: Port that host will be listening on

#### /unregister_client
- Description: Unregister a client, specifying the port. The sender's IP address will be detected and used as the client's IP address.
- Arguments:
  - 0
    - Type: Int
    - Description: Client port
  
#### /unregister_client_with_ip_address
- Description: Unregister a client, specifying the IP address and port.
- Arguments:
  - 0
    - Type: String
    - Description: Host name or IP address of client
  - 1
    - Type: Int
    - Description: Client port

## Preset Handling

### Loading Presets

#### /load_preset
- Description: Load a preset from one of Nymphes' memory slots
- Arguments:
  - 0
    - Type: String
    - Description: Preset Type
    - Possible Values: 'user' or 'factory'
  - 1
    - Type: String
    - Description: Preset Bank 
    - Possible Values: 'A' through 'G'
  - 2
    - Type: Int
    - Description: Preset Number 
    - Possible Values: 1 through 7

#### /load_file
- Description: Load a .txt preset file or .syx sysex file from disk and send to Nymphes via SYSEX using a non-persistent import
- Arguments:
  - 0
    - Type: String
    - Description: Filepath to load

#### /load_init_file
- Description: Load the init preset file (init.txt). This is the same preset that is automatically loaded when Nymphes first connects.
- Arguments: None

### Saving to Preset Slots

#### /save_to_preset
- Description: Save the current settings to one of Nymphes' preset slots
- Arguments:
  - 0
    - Type: String
    - Description: Preset Type
    - Possible Values: 'user' or 'factory'
  - 1
    - Type: String
    - Description: Preset Bank 
    - Possible Values: 'A' through 'G'
  - 2
    - Type: Int
    - Description: Preset Number 
    - Possible Values: 1 through 7

#### /load_file_to_preset
- Description: Load a preset file from disk and send via SYSEX to Nymphes, writing to a preset slot
- Arguments:
  - 0
    - Type: String
    - Description: Filepath of preset to load
  - 1
    - Type: String
    - Description: Preset Type
    - Possible Values: 'user' or 'factory'
  - 2
    - Type: String
    - Description: Preset Bank 
    - Possible Values: 'A' through 'G'
  - 3
    - Type: Int
    - Description: Preset Number 
    - Possible Values: 1 through 7

### Saving to Preset Files

#### /save_to_file
- Description: Save to a preset file on disk
- Arguments:
  - 0
    - Type: String
    - Description: Destination filepath

#### /save_preset_to_file
- Description: Write the contents of a preset slot to a file on disk
- Arguments:
  - 0
    - Type: String
    - Description: Destination filepath
  - 1
    - Type: String
    - Description: Preset Type
    - Possible Values: 'user' or 'factory'
  - 2
    - Type: String
    - Description: Preset Bank 
    - Possible Values: 'A' through 'G'
  - 3
    - Type: Int
    - Description: Preset Number 
    - Possible Values: 1 through 7

### Other

#### /request_preset_dump
- Description: Send a dump request to Nymphes via SYSEX. This causes Nymphes to send all of its presets via SYSEX messages
- Arguments: None

## MIDI Port Control

#### /connect_nymphes
- Description: Connect to Nymphes using the specified MIDI Input and Output Ports
- Arguments:
  - 0
    - Type: String
    - Description: The name of the MIDI Input port for Nymphes (as reported by mido.get_input_names())
  - 1
    - Type: String
    - Description: The name of the MIDI Output port for Nymphes (as reported by mido.get_output_names())

#### /disconnect_nymphes
- Description: Disconnect from Nymphes MIDI ports
- Arguments: None

#### /connect_midi_input
- Description: Connect the specified MIDI Input Port. Messages received from connected MIDI Input Ports are will be interpreted by nymphes-midi and passed on to Nymphes.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the port (as reported by mido.get_input_names())

#### /disconnect_midi_input
- Description: Disconnect the specified MIDI Input Port. Messages will no longer be received from the port.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the port (as reported by mido.get_input_names())

#### /enable_midi_feedback_suppression
- Description: Enable MIDI feedback suppression, ignoring any received copies of MIDI messages recently sent to MIDI output ports
- Arguments: None

#### /disable_midi_feedback_suppression
- Description: Disable MIDI feedback suppression
- Arguments: None

#### /connect_midi_output
- Description: Connect the specified MIDI Output Port. Messages from Nymphes and software clients will be passed on to connected MIDI Output Ports.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the port (as reported by mido.get_output_names())

#### /disconnect_midi_output
- Description: Disconnect the specified MIDI Output Port. Messages will no longer be sent to the port.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the port (as reported by mido.get_output_names())

## Setting Nymphes Parameters

### Oscillator Settings

#### Wave Shape
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /osc/wave/value
  - /osc/wave/mod_wheel
  - /osc/wave/velocity
  - /osc/wave/aftertouch
  - /osc/wave/lfo2

#### Pulsewidth
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /osc/pulsewidth/value  
  - /osc/pulsewidth/mod_wheel
  - /osc/pulsewidth/velocity
  - /osc/pulsewidth/aftertouch
  - /osc/pulsewidth/lfo2

#### Voice Mode
- Address: /osc/voice_mode/value
- Value Type: Int
    - 0: Polyphonic
      - 6 note polyphony
      - 1 voice per note
    - 1: Unison Mode A
      - 1 note polyphony
      - 6 voices in unison
    - 2: Unison Mode B
      - 1 note polyphony
      - 4 voices in unison
    - 3: Tri
      - 3 note polyphony
      - 2 voices per note
    - 4: Duo
      - 2 note polyphony
      - 3 voices per note
    - 5: Monophonic
      - 1 note polyphony
      - 1 voice per note

#### Legato
- Address: /osc/legato/value
- Value Type: Int
  - 0: Off
  - 127: On

### Pitch Settings

#### Detune
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /pitch/detune/value   
  - /pitch/detune/mod_wheel
  - /pitch/detune/velocity
  - /pitch/detune/aftertouch
  - /pitch/detune/lfo2

#### Chord Selector
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /pitch/chord/value
  - /pitch/chord/mod_wheel
  - /pitch/chord/velocity
  - /pitch/chord/aftertouch
  - /pitch/chord/lfo2

#### Pitch EG Depth
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /pitch/eg/value
  - /pitch/eg/mod_wheel
  - /pitch/eg/velocity
  - /pitch/eg/aftertouch
  - /pitch/eg/lfo2

#### Pitch LFO1 Depth
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /pitch/lfo1/value
  - /pitch/lfo1/mod_wheel
  - /pitch/lfo1/velocity
  - /pitch/lfo1/aftertouch
  - /pitch/lfo1/lfo2

#### Glide
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /pitch/glide/value   
  - /pitch/glide/mod_wheel
  - /pitch/glide/velocity
  - /pitch/glide/aftertouch
  - /pitch/glide/lfo2

### Amp EG Settings

#### Attack
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /amp_eg/attack/value   
  - /amp_eg/attack/mod_wheel
  - /amp_eg/attack/velocity
  - /amp_eg/attack/aftertouch
  - /amp_eg/attack/lfo2

#### Decay
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /amp_eg/decay/value   
  - /amp_eg/decay/mod_wheel
  - /amp_eg/decay/velocity
  - /amp_eg/decay/aftertouch
  - /amp_eg/decay/lfo2

#### Sustain
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /amp_eg/sustain/value   
  - /amp_eg/sustain/mod_wheel
  - /amp_eg/sustain/velocity
  - /amp_eg/sustain/aftertouch
  - /amp_eg/sustain/lfo2

#### Release
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /amp_eg/release/value   
  - /amp_eg/release/mod_wheel
  - /amp_eg/release/velocity
  - /amp_eg/release/aftertouch
  - /amp_eg/release/lfo2

### Mix Settings

#### Oscillator Level
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /mix/osc/value   
  - /mix/osc/mod_wheel
  - /mix/osc/velocity
  - /mix/osc/aftertouch
  - /mix/osc/lfo2

#### Sub Level
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /mix/sub/value   
  - /mix/sub/mod_wheel
  - /mix/sub/velocity
  - /mix/sub/aftertouch
  - /mix/sub/lfo2

#### Noise Level
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /mix/noise/value   
  - /mix/noise/mod_wheel
  - /mix/noise/velocity
  - /mix/noise/aftertouch
  - /mix/noise/lfo2

#### Main Level
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Address: /mix/level/value

### LPF Settings

#### Cutoff
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lpf/cutoff/value   
  - /lpf/cutoff/mod_wheel
  - /lpf/cutoff/velocity
  - /lpf/cutoff/aftertouch
  - /lpf/cutoff/lfo2

#### Resonance
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lpf/resonance/value   
  - /lpf/resonance/mod_wheel
  - /lpf/resonance/velocity
  - /lpf/resonance/aftertouch
  - /lpf/resonance/lfo2

#### Tracking
- - Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lpf/tracking/value   
  - /lpf/tracking/mod_wheel
  - /lpf/tracking/velocity
  - /lpf/tracking/aftertouch
  - /lpf/tracking/lfo2

#### Envelope Depth
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lpf/eg/value   
  - /lpf/eg/mod_wheel
  - /lpf/eg/velocity
  - /lpf/eg/aftertouch
  - /lpf/eg/lfo2

#### LFO1 Depth
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lpf/lfo1/value   
  - /lpf/lfo1/mod_wheel
  - /lpf/lfo1/velocity
  - /lpf/lfo1/aftertouch
  - /lpf/lfo1/lfo2

### HPF Settings

#### Cutoff
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /hpf/cutoff/value   
  - /hpf/cutoff/mod_wheel
  - /hpf/cutoff/velocity
  - /hpf/cutoff/aftertouch
  - /hpf/cutoff/lfo2

### Filter Envelope Settings

#### Attack
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /filter_eg/attack/value   
  - /filter_eg/attack/mod_wheel
  - /filter_eg/attack/velocity
  - /filter_eg/attack/aftertouch
  - /filter_eg/attack/lfo2

#### Decay
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /filter_eg/decay/value   
  - /filter_eg/decay/mod_wheel
  - /filter_eg/decay/velocity
  - /filter_eg/decay/aftertouch
  - /filter_eg/decay/lfo2

#### Sustain
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /filter_eg/sustain/value   
  - /filter_eg/sustain/mod_wheel
  - /filter_eg/sustain/velocity
  - /filter_eg/sustain/aftertouch
  - /filter_eg/sustain/lfo2

#### Release
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /filter_eg/release/value   
  - /filter_eg/release/mod_wheel
  - /filter_eg/release/velocity
  - /filter_eg/release/aftertouch
  - /filter_eg/release/lfo2

### LFO1 (Pitch-Filter LFO) Settings

#### Rate
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo1/rate/value   
  - /lfo1/rate/mod_wheel
  - /lfo1/rate/velocity
  - /lfo1/rate/aftertouch
  - /lfo1/rate/lfo2

#### Wave
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo1/wave/value   
  - /lfo1/wave/mod_wheel
  - /lfo1/wave/velocity
  - /lfo1/wave/aftertouch
  - /lfo1/wave/lfo2

#### Delay
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo1/delay/value   
  - /lfo1/delay/mod_wheel
  - /lfo1/delay/velocity
  - /lfo1/delay/aftertouch
  - /lfo1/delay/lfo2

#### Fade
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo1/fade/value   
  - /lfo1/fade/mod_wheel
  - /lfo1/fade/velocity
  - /lfo1/fade/aftertouch
  - /lfo1/fade/lfo2

#### Type
- Address: /lfo1/type/value
- Value Type: Int
  - 0: BPM
  - 1: Low
  - 2: High
  - 3: Track

#### Key Sync
- Address: /lfo1/key_sync/value
- Value Type: int
  - 0: Off
  - 1: On

### LFO2 Settings

#### Rate
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo2/rate/value   
  - /lfo2/rate/mod_wheel
  - /lfo2/rate/velocity
  - /lfo2/rate/aftertouch
  - /lfo2/rate/lfo2

#### Wave
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo2/wave/value   
  - /lfo2/wave/mod_wheel
  - /lfo2/wave/velocity
  - /lfo2/wave/aftertouch
  - /lfo2/wave/lfo2

#### Delay
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo2/delay/value   
  - /lfo2/delay/mod_wheel
  - /lfo2/delay/velocity
  - /lfo2/delay/aftertouch
  - /lfo2/delay/lfo2

#### Fade
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo2/fade/value   
  - /lfo2/fade/mod_wheel
  - /lfo2/fade/velocity
  - /lfo2/fade/aftertouch
  - /lfo2/fade/lfo2

#### Type
- Address: /lfo2/type/value
- Value Type: Int
  - 0: BPM
  - 1: Low
  - 2: High
  - 3: Track

#### Key Sync
- Address: /lfo2/key_sync/value
- Value Type: int
  - 0: Off
  - 1: On

### Reverb Settings

#### Size
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /reverb/size/value   
  - /reverb/size/mod_wheel
  - /reverb/size/velocity
  - /reverb/size/aftertouch
  - /reverb/size/lfo2

#### Decay
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /reverb/decay/value   
  - /reverb/decay/mod_wheel
  - /reverb/decay/velocity
  - /reverb/decay/aftertouch
  - /reverb/decay/lfo2

#### Filter
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /reverb/filter/value   
  - /reverb/filter/mod_wheel
  - /reverb/filter/velocity
  - /reverb/filter/aftertouch
  - /reverb/filter/lfo2

### Mix Settings
- Value Type: 
  - Float (0.0 to 127.0) 
  - Int (0 to 127)
- Addresses:
  - /reverb/mix/value   
  - /reverb/mix/mod_wheel
  - /reverb/mix/velocity
  - /reverb/mix/aftertouch
  - /reverb/mix/lfo2

### Chord 0 Settings
- Value Type:
  - Int
- Value Range:
  - Root values are 0 to 127
  - Semitone values are -127 to 127
- Addresses:
  - /chord_0/root/value
  - /chord_0/semi_1/value
  - /chord_0/semi_2/value
  - /chord_0/semi_3/value
  - /chord_0/semi_4/value
  - /chord_0/semi_5/value

### Chord 1 Settings
- Value Type:
  - Int
- Value Range:
  - Root values are 0 to 127
  - Semitone values are -127 to 127
- Addresses:
  - /chord_1/root/value
  - /chord_1/semi_1/value
  - /chord_1/semi_2/value
  - /chord_1/semi_3/value
  - /chord_1/semi_4/value
  - /chord_1/semi_5/value

### Chord 2 Settings
- Value Type:
  - Int
- Value Range:
  - Root values are 0 to 127
  - Semitone values are -127 to 127
- Addresses:
  - /chord_2/root/value
  - /chord_2/semi_1/value
  - /chord_2/semi_2/value
  - /chord_2/semi_3/value
  - /chord_2/semi_4/value
  - /chord_2/semi_5/value

### Chord 3 Settings
- Value Type:
  - Int
- Value Range:
  - Root values are 0 to 127
  - Semitone values are -127 to 127
- Addresses:
  - /chord_3/root/value
  - /chord_3/semi_1/value
  - /chord_3/semi_2/value
  - /chord_3/semi_3/value
  - /chord_3/semi_4/value
  - /chord_3/semi_5/value

### Chord 4 Settings
- Value Type:
  - Int
- Value Range:
  - Root values are 0 to 127
  - Semitone values are -127 to 127
- Addresses:
  - /chord_4/root/value
  - /chord_4/semi_1/value
  - /chord_4/semi_2/value
  - /chord_4/semi_3/value
  - /chord_4/semi_4/value
  - /chord_4/semi_5/value

### Chord 5 Settings
- Value Type:
  - Int
- Value Range:
  - Root values are 0 to 127
  - Semitone values are -127 to 127
- Addresses:
  - /chord_5/root/value
  - /chord_5/semi_1/value
  - /chord_5/semi_2/value
  - /chord_5/semi_3/value
  - /chord_5/semi_4/value
  - /chord_5/semi_5/value

### Chord 6 Settings
- Value Type:
  - Int
- Value Range:
  - Root values are 0 to 127
  - Semitone values are -127 to 127
- Addresses:
  - /chord_6/root/value
  - /chord_6/semi_1/value
  - /chord_6/semi_2/value
  - /chord_6/semi_3/value
  - /chord_6/semi_4/value
  - /chord_6/semi_5/value

### Chord 7 Settings
- Value Type:
  - Int
- Value Range:
  - Root values are 0 to 127
  - Semitone values are -127 to 127
- Addresses:
  - /chord_7/root/value
  - /chord_7/semi_1/value
  - /chord_7/semi_2/value
  - /chord_7/semi_3/value
  - /chord_7/semi_4/value
  - /chord_7/semi_5/value


## Performance Controls

#### /mod_wheel
- Description: Send a mod wheel MIDI Control Change message (CC 1) to Nymphes and connected MIDI Output Ports
- Arguments:
  - 0
    - Type: Int
    - Range: 0 to 127

#### /aftertouch
- Description: Send a channel aftertouch MIDI message to Nymphes and connected MIDI Output Ports
- Arguments:
  - 0
    - Type: Int
    - Range: 0 to 127

#### /sustain_pedal
- Description: Sustain Pedal status
- Arguments:
  - 0
    - Type: Int
    - Values:
      - 0: Off
      - 1: On

## Other Settings and Controls

#### /set_nymphes_midi_channel
- Description: Inform nymphes-osc of the MIDI channel that Nymphes is using
- Arguments:
  - 0
    - Type: Int
    - Range: 1 to 16
    - Description: The MIDI channel

# OSC Messages Sent to Clients

## OSC Client Events

#### /client_registered
- Description: An OSC client has just been registered
- Arguments:
  - 0
    - Type: String
    - Description: Host name or IP address of client
  - 1
    - Type: Int
    - Description: Port that host is listening on

#### /client_unregistered
- Description: An OSC client has just been unregistered
- Arguments:
  - 0
    - Type: String
    - Description: Host name or IP address of client
    - 1
      - Type: Int
      - Description: Port of client 

## Preset Events

### Loading Presets

#### /loaded_preset
- Description: A preset has just been loaded on Nymphes
- Arguments:
  - 0
    - Type: String
    - Description: Type of preset
      - 'user' or 'factory'
  - 1
    - Type: String
    - Description: Bank
      - Possible Values: 'A', 'B', 'C', 'D', 'E', 'F', 'G'
  - 2
    - Type: Int
    - Description: Preset Number
      - Possible Values: 1, 2, 3, 4, 5, 6, 7

#### /loaded_file
- Description: A preset file has just been loaded
- Arguments:
  - 0
    - Type: String
    - Description: Filepath of loaded file

#### /loaded_init_file
- Description: The init preset file (init.txt) has just been loaded
- Arguments:
  - 0
    - Type: String
    - Description: Filepath of the file
    
### Saving to Preset Slots

#### /saved_to_preset
- Description: The current settings have been written into a preset slot.
- Arguments:
  - 0
    - Type: String
    - Description: Type of preset
      - 'user' or 'factory'
  - 1
    - Type: String
    - Description: Bank
      - Possible Values: 'A', 'B', 'C', 'D', 'E', 'F', 'G'
  - 2
    - Type: Int
    - Description: Preset Number
      - Possible Values: 1, 2, 3, 4, 5, 6, 7

#### /loaded_file_to_preset
- Description: A file has just been loaded and written into a Nymphes preset slot.
- Arguments:
  - 0
    - Type: String
    - Description: Filepath of loaded preset
  - 1
    - Type: String
    - Description: Type of preset
      - 'user' or 'factory'
  - 2
    - Type: String
    - Description: Bank
      - Possible Values: 'A', 'B', 'C', 'D', 'E', 'F', 'G'
  - 3
    - Type: Int
    - Description: Preset Number
      - Possible Values: 1, 2, 3, 4, 5, 6, 7

### Saving to Preset Files

#### /saved_to_file
- Description: The current settings have been saved to a preset file
- Arguments:
  - 0
    - Type: String
    - Description: Filepath of saved preset

#### /saved_preset_to_file
- Description: The contents of a preset slot have been saved to a file
- Arguments:
  - 0
    - Type: String
    - Description: Filepath of loaded preset
  - 1
    - Type: String
    - Description: Type of preset
      - 'user' or 'factory'
  - 2
    - Type: String
    - Description: Bank
      - Possible Values: 'A', 'B', 'C', 'D', 'E', 'F', 'G'
  - 3
    - Type: Int
    - Description: Preset Number
      - Possible Values: 1, 2, 3, 4, 5, 6, 7

### Other

#### /requested_preset_dump
- Description: A full preset dump has been requested from Nymphes
- Arguments: None

#### /received_preset_dump_from_nymphes
- Description: Received a preset from Nymphes as a persistent import, so this is a preset dump
- Arguments:
  - 0
    - Type: String
    - Description: Type of preset
      - 'user' or 'factory'
  - 1
    - Type: String
    - Description: Bank
      - Possible Values: 'A', 'B', 'C', 'D', 'E', 'F', 'G'
  - 2
    - Type: Int
    - Description: Preset Number
      - Possible Values: 1, 2, 3, 4, 5, 6, 7

#### /loaded_preset_dump_from_midi_input_port
- Description: A preset has been received via SYSEX from a MIDI Input Port.
- Arguments:
  - 0
    - Type: String
    - Description: Name of the MIDI input port
  - 1
    - Type: String
    - Description: Type of preset
      - 'user' or 'factory'
  - 2
    - Type: String
    - Description: Bank
      - Possible Values: 'A', 'B', 'C', 'D', 'E', 'F', 'G'
  - 3
    - Type: Int
    - Description: Preset Number
      - Possible Values: 1, 2, 3, 4, 5, 6, 7

#### /saved_preset_dump_from_midi_input_port_to_preset
- Description: Received a persistent preset from a MIDI Input port and passed it on to Nymphes, writing it to a memory slot
- Arguments:
  - 0
    - Type: String
    - Description: Name of the MIDI input port
  - 1
    - Type: String
    - Description: Type of preset
      - 'user' or 'factory'
  - 2
    - Type: String
    - Description: Bank
      - Possible Values: 'A', 'B', 'C', 'D', 'E', 'F', 'G'
  - 3
    - Type: Int
    - Description: Preset Number
      - Possible Values: 1, 2, 3, 4, 5, 6, 7

#### /unsaved_changes
- Description: There are unsaved changes since the current preset was loaded or saved.
- Arguments: None

## MIDI Port Events

### Nymphes Connection

#### /nymphes_midi_input_detected
- Description: A new Nymphes MIDI input port has been detected
- Arguments:
  - 0
    - Type: String
    - Description: The name of the newly-detected MIDI input port

#### /nymphes_midi_input_no_longer_detected
- Description: A previously-detected Nymphes MIDI input port is no longer detected.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the Nymphes MIDI input port that is no longer detected

#### /nymphes_midi_output_detected
- Description: A new Nymphes MIDI output port has been detected
- Arguments:
  - 0
    - Type: String
    - Description: The name of the newly-detected Nymphes MIDI output port

#### /nymphes_midi_output_no_longer_detected
- Description: A previously-detected Nymphes MIDI output port is no longer detected.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the Nymphes MIDI output port that is no longer detected 

#### /nymphes_connected
- Description: The Nymphes synthesizer has just been connected
- Arguments:
  - 0
    - Type: String
    - Description: The name of the MIDI input port for messages from Nymphes
  - 1
    - Type: String
    - Description: The name of the MIDI output port for messages to Nymphes

#### /nymphes_disconnected
- Description: The Nymphes synthesizer has just been disconnected
- Arguments: None

### MIDI Input Ports 

#### /midi_input_detected
- Description: A new MIDI input port has been detected
- Arguments:
  - 0
    - Type: String
    - Description: The name of the newly-detected MIDI input port

#### /midi_input_no_longer_detected
- Description: A previously-detected MIDI input port is no longer detected.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the MIDI input port that is no longer detected 

#### /midi_input_connected
- Description: A MIDI input port has been connected
- Arguments:
  - 0
    - Type: String
    - Description: The name of the MIDI input port

#### /midi_input_disconnected
- Description: A MIDI input port has been disconnected
- Arguments:
  - 0
    - Type: String
    - Description: The name of the MIDI input port

#### /midi_feedback_suppression_enabled
- Description: MIDI feedback suppression has been enabled, ignoring received copies of MIDI messages that were recently sent to MIDI output ports
- Arguments: None

#### /midi_feedback_suppression_disabled
- Description: MIDI feedback suppression has been disabled.
- Arguments: None

#### /midi_feedback_detected
- Description: MIDI feedback has been detected. Ie: A copy of a recently-sent MIDI messages has been received.
- Arguments: None

### MIDI Output Ports

#### /midi_output_detected
- Description: A new MIDI output port has been detected
- Arguments:
  - 0
    - Type: String
    - Description: The name of the newly-detected MIDI output port

#### /midi_output_no_longer_detected
- Description: A previously-detected MIDI output port is no longer detected.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the MIDI output port that is no longer detected

#### /midi_output_connected
- Description: A MIDI output port has been connected
- Arguments:
  - 0
    - Type: String
    - Description: The name of the MIDI output port

#### /midi_output_disconnected
- Description: A MIDI output port has been disconnected
- Arguments:
  - 0
    - Type: String
    - Description: The name of the MIDI output port

## Performance Controls

#### /mod_wheel
- Description: A mod wheel MIDI Control Change Message (CC 1) has been received from a MIDI Input Port
- Arguments:
  - 0
    - Type: Int
    - Range: 0 to 127

#### /aftertouch
- Description: A channel aftertouch MIDI message has been received from a MIDI Input Port
- Arguments:
  - 0
    - Description: Aftertouch Amount
    - Type: Int
    - Range: 0 to 127

#### /poly_aftertouch
- Description: A poly aftertouch MIDI message has been received from a MIDI Input Port
- Arguments:
  - 0
    - Description: MIDI Channel
    - Type: Int
    - Range: 1 to 16
  - 1
    - Description: Aftertouch Amount
    - Type: Int
    - Range: 0 to 127

#### /velocity
- Description: The velocity value of the most recently-received MIDI note-on message. nymphes_osc will output this message whenever a new note_on message is received. We only send this OSC message. We do not respond to incoming messages of this type.
- Arguments:
  - 0
    - Type: Int
    - Range: 0 to 127

#### /sustain_pedal
- Description: Sustain Pedal status
- Arguments:
  - 0
    - Type: Int
    - Values:
      - 0: Off
      - 1: On

## Other Messages

#### /status
- Description: A general status message. These messages mirror those output on the console of the machine running the nymphes_osc application
- Arguments:
  - 0
    - Type: String

#### /error
- Description: An error message. These messages mirror those output on the console of the machine running the nymphes_osc application
- Arguments:
  - 0
    - Type: String
    - Description: Error Message
  - 1
    - Type: String
    - Description: Error Message Extra Detail

#### /nymphes_midi_channel_changed
- Description: The MIDI channel that Nymphes uses changed
- Arguments:
  - 0
    - Type: Int
    - Range: 1 to 16
    - Description: The MIDI channel

#### /presets_directory_path
- Description: The absolute path to the presets directory. Sent to clients upon registering.
- Arguments:
  - 0
    - Type: String
 
