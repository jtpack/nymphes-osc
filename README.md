# Nymphes OSC Bridge

### A software object that provides OSC control of the Dreadbox Nymphes MIDI synthesizer

# OSC Messages Accepted from Clients

## OSC Client Handling

### /register_client
- Description: Register an OSC client with the OSC server. Only registered OSC clients receive any messages from nymphes-osc. The sender's IP address will be detected and used as the client's IP address.
- Arguments:
  - 0
    - Type: Int
    - Description: Port that host will be listening on
    
  
### /register_client_with_ip_address
- Description: Register an OSC client, but specify the IP address to use.
- Arguments:
  - 0
    - Type: String
    - Description: Host name or IP address (ie: 192.168.0.52)
  - 1
    - Type: Int
    - Description: Port that host will be listening on


### /unregister_client
- Description: Unregister a client. The client's IP address will be that of the sender.
- Arguments:
  - 0
    - Type: Int
    - Description: Client port
  
### /unregister_client_with_ip_address
- Description: Unregister a client, specifying the client's IP address rather than using that of the sender.
- Arguments:
  - 0
    - Type: String
    - Description: Host name or IP address of client
  - 1
    - Type: Int
    - Description: Client port

## Setting Nymphes Parameters

### Oscillator Settings

#### Wave Shape
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /osc/wave/value
  - /osc/wave/mod_wheel
  - /osc/wave/velocity
  - /osc/wave/aftertouch
  - /osc/wave/lfo2

#### Pulsewidth
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /osc/pulsewidth/value  
  - /osc/pulsewidth/mod_wheel
  - /osc/pulsewidth/velocity
  - /osc/pulsewidth/aftertouch
  - /osc/pulsewidth/lfo2

#### Voice Mode
- Address: /osc/voice_mode
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
- Address: /osc/legato
- Value Type: Int
  - 0: Off
  - 1: On

### Pitch Settings

#### Detune
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /pitch/detune/value   
  - /pitch/detune/mod_wheel
  - /pitch/detune/velocity
  - /pitch/detune/aftertouch
  - /pitch/detune/lfo2

#### Chord Selector
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /pitch/chord/value
  - /pitch/chord/mod_wheel
  - /pitch/chord/velocity
  - /pitch/chord/aftertouch
  - /pitch/chord/lfo2

#### Pitch EG Depth
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /pitch/eg/value
  - /pitch/eg/mod_wheel
  - /pitch/eg/velocity
  - /pitch/eg/aftertouch
  - /pitch/eg/lfo2

#### Pitch LFO1 Depth
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /pitch/lfo1/value
  - /pitch/lfo1/mod_wheel
  - /pitch/lfo1/velocity
  - /pitch/lfo1/aftertouch
  - /pitch/lfo1/lfo2

#### Glide
- Value Type: 
  - Float (0.0 to 1.0) 
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
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /amp_eg/attack/value   
  - /amp_eg/attack/mod_wheel
  - /amp_eg/attack/velocity
  - /amp_eg/attack/aftertouch
  - /amp_eg/attack/lfo2

#### Decay
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /amp_eg/decay/value   
  - /amp_eg/decay/mod_wheel
  - /amp_eg/decay/velocity
  - /amp_eg/decay/aftertouch
  - /amp_eg/decay/lfo2

#### Sustain
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /amp_eg/sustain/value   
  - /amp_eg/sustain/mod_wheel
  - /amp_eg/sustain/velocity
  - /amp_eg/sustain/aftertouch
  - /amp_eg/sustain/lfo2

#### Release
- Value Type: 
  - Float (0.0 to 1.0) 
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
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /mix/osc/value   
  - /mix/osc/mod_wheel
  - /mix/osc/velocity
  - /mix/osc/aftertouch
  - /mix/osc/lfo2

#### Sub Level
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /mix/sub/value   
  - /mix/sub/mod_wheel
  - /mix/sub/velocity
  - /mix/sub/aftertouch
  - /mix/sub/lfo2

#### Noise Level
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /mix/noise/value   
  - /mix/noise/mod_wheel
  - /mix/noise/velocity
  - /mix/noise/aftertouch
  - /mix/noise/lfo2

#### Main Level
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Address: /mix/level

### LPF Settings

#### Cutoff
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /lpf/cutoff/value   
  - /lpf/cutoff/mod_wheel
  - /lpf/cutoff/velocity
  - /lpf/cutoff/aftertouch
  - /lpf/cutoff/lfo2

#### Resonance
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /lpf/resonance/value   
  - /lpf/resonance/mod_wheel
  - /lpf/resonance/velocity
  - /lpf/resonance/aftertouch
  - /lpf/resonance/lfo2

#### Tracking
- - Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /lpf/tracking/value   
  - /lpf/tracking/mod_wheel
  - /lpf/tracking/velocity
  - /lpf/tracking/aftertouch
  - /lpf/tracking/lfo2

#### Envelope Depth
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /lpf/eg/value   
  - /lpf/eg/mod_wheel
  - /lpf/eg/velocity
  - /lpf/eg/aftertouch
  - /lpf/eg/lfo2

#### LFO1 Depth
- Value Type: 
  - Float (0.0 to 1.0) 
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
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /hpf/cutoff/value   
  - /hpf/cutoff/mod_wheel
  - /hpf/cutoff/velocity
  - /hpf/cutoff/aftertouch
  - /hpf/cutoff/lfo2

### Pitch-Filter Envelope

#### Attack
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /filter_eg/attack/value   
  - /filter_eg/attack/mod_wheel
  - /filter_eg/attack/velocity
  - /filter_eg/attack/aftertouch
  - /filter_eg/attack/lfo2

#### Decay
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /filter_eg/decay/value   
  - /filter_eg/decay/mod_wheel
  - /filter_eg/decay/velocity
  - /filter_eg/decay/aftertouch
  - /filter_eg/decay/lfo2

#### Sustain
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /filter_eg/sustain/value   
  - /filter_eg/sustain/mod_wheel
  - /filter_eg/sustain/velocity
  - /filter_eg/sustain/aftertouch
  - /filter_eg/sustain/lfo2

#### Release
- Value Type: 
  - Float (0.0 to 1.0) 
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
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo1/rate/value   
  - /lfo1/rate/mod_wheel
  - /lfo1/rate/velocity
  - /lfo1/rate/aftertouch
  - /lfo1/rate/lfo2

#### Wave
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo1/wave/value   
  - /lfo1/wave/mod_wheel
  - /lfo1/wave/velocity
  - /lfo1/wave/aftertouch
  - /lfo1/wave/lfo2

#### Delay
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo1/delay/value   
  - /lfo1/delay/mod_wheel
  - /lfo1/delay/velocity
  - /lfo1/delay/aftertouch
  - /lfo1/delay/lfo2

#### Fade
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo1/fade/value   
  - /lfo1/fade/mod_wheel
  - /lfo1/fade/velocity
  - /lfo1/fade/aftertouch
  - /lfo1/fade/lfo2

#### Type
- Address: /lfo1/type
- Value Type: Int
  - 0: BPM
  - 1: Low
  - 2: High
  - 3: Track

#### Key Sync
- Address: /lfo1/key_sync
- Value Type: int
  - 0: Off
  - 1: On

### LFO2

#### Rate
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo2/rate/value   
  - /lfo2/rate/mod_wheel
  - /lfo2/rate/velocity
  - /lfo2/rate/aftertouch
  - /lfo2/rate/lfo2

#### Wave
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo2/wave/value   
  - /lfo2/wave/mod_wheel
  - /lfo2/wave/velocity
  - /lfo2/wave/aftertouch
  - /lfo2/wave/lfo2

#### Delay
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo2/delay/value   
  - /lfo2/delay/mod_wheel
  - /lfo2/delay/velocity
  - /lfo2/delay/aftertouch
  - /lfo2/delay/lfo2

#### Fade
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /lfo2/fade/value   
  - /lfo2/fade/mod_wheel
  - /lfo2/fade/velocity
  - /lfo2/fade/aftertouch
  - /lfo2/fade/lfo2

#### Type
- Address: /lfo2/type
- Value Type: Int
  - 0: BPM
  - 1: Low
  - 2: High
  - 3: Track

#### Key Sync
- Address: /lfo2/key_sync
- Value Type: int
  - 0: Off
  - 1: On

### Reverb

#### Size
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /reverb/size/value   
  - /reverb/size/mod_wheel
  - /reverb/size/velocity
  - /reverb/size/aftertouch
  - /reverb/size/lfo2

#### Decay
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /reverb/decay/value   
  - /reverb/decay/mod_wheel
  - /reverb/decay/velocity
  - /reverb/decay/aftertouch
  - /reverb/decay/lfo2

#### Filter
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /reverb/filter/value   
  - /reverb/filter/mod_wheel
  - /reverb/filter/velocity
  - /reverb/filter/aftertouch
  - /reverb/filter/lfo2

#### Mix
- Value Type: 
  - Float (0.0 to 1.0) 
  - Int (0 to 127)
- Addresses:
  - /reverb/mix/value   
  - /reverb/mix/mod_wheel
  - /reverb/mix/velocity
  - /reverb/mix/aftertouch
  - /reverb/mix/lfo2

### Chord 1 Settings
- Value Type:
  - Int (0 to 127)
- Addresses:
  - /chord_1/root
  - /chord_1/semi_1
  - /chord_1/semi_2
  - /chord_1/semi_3
  - /chord_1/semi_4
  - /chord_1/semi_5

### Chord 2 Settings
- Value Type:
  - Int (0 to 127)
- Addresses:
  - /chord_2/root
  - /chord_2/semi_1
  - /chord_2/semi_2
  - /chord_2/semi_3
  - /chord_2/semi_4
  - /chord_2/semi_5

### Chord 3 Settings
- Value Type:
  - Int (0 to 127)
- Addresses:
  - /chord_3/root
  - /chord_3/semi_1
  - /chord_3/semi_2
  - /chord_3/semi_3
  - /chord_3/semi_4
  - /chord_3/semi_5

### Chord 4 Settings
- Value Type:
  - Int (0 to 127)
- Addresses:
  - /chord_4/root
  - /chord_4/semi_1
  - /chord_4/semi_2
  - /chord_4/semi_3
  - /chord_4/semi_4
  - /chord_4/semi_5

### Chord 5 Settings
- Value Type:
  - Int (0 to 127)
- Addresses:
  - /chord_5/root
  - /chord_5/semi_1
  - /chord_5/semi_2
  - /chord_5/semi_3
  - /chord_5/semi_4
  - /chord_5/semi_5

### Chord 6 Settings
- Value Type:
  - Int (0 to 127)
- Addresses:
  - /chord_6/root
  - /chord_6/semi_1
  - /chord_6/semi_2
  - /chord_6/semi_3
  - /chord_6/semi_4
  - /chord_6/semi_5

### Chord 7 Settings
- Value Type:
  - Int (0 to 127)
- Addresses:
  - /chord_7/root
  - /chord_7/semi_1
  - /chord_7/semi_2
  - /chord_7/semi_3
  - /chord_7/semi_4
  - /chord_7/semi_5

### Chord 8 Settings
- Value Type:
  - Int (0 to 127)
- Addresses:
  - /chord_8/root
  - /chord_8/semi_1
  - /chord_8/semi_2
  - /chord_8/semi_3
  - /chord_8/semi_4
  - /chord_8/semi_5

## Preset Handling

### /load_preset
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
 
### /load_preset_file
- Description: Load a preset file from disk and send via SYSEX to Nymphes
- Arguments:
  - 0
    - Type: String
    - Description: Filepath of preset to load
  
### /load_preset_file_to_memory_slot
- Description: Load a preset file from disk and send via SYSEX to Nymphes, overwriting a memory slot
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
      
### /save_preset_file
- Description: Save current settings to a preset file on disk
- Arguments:
  - 0
    - Type: String
    - Description: Destination filepath

## MIDI Port Control

### /open_midi_input_port
- Description: Open the specified MIDI Input Port. Messages received from connected MIDI Input Ports are will be interpreted by nymphes-midi and passed on to Nymphes.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the port (as reported by mido.get_input_names())

### /close_midi_input_port
- Description: Close the specified MIDI Input Port. Messages will no longer be received from the port.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the port (as reported by mido.get_input_names())

### /open_midi_output_port
- Description: Open the specified MIDI Output Port. Messages from Nymphes and software clients will be passed on to connected MIDI Output Ports.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the port (as reported by mido.get_output_names())

### /close_midi_output_port
- Description: Close the specified MIDI Output Port. Messages will no longer be sent to the port.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the port (as reported by mido.get_output_names())

## Other Settings and Controls

### /set_nymphes_midi_channel
- Description: Inform nymphes-osc of the MIDI channel that Nymphes is using
- Arguments:
  - 0
    - Type: Int
    - Range: 1 to 16
    - Description: The MIDI channel
  
### /mod_wheel
- Description: Send a mod wheel MIDI Control Change message (CC 1) to Nymphes and connected MIDI Output Ports
- Arguments:
  - 0
    - Type: Int
    - Range: 0 to 127

### /aftertouch
- Description: Send a channel aftertouch MIDI message to Nymphes and connected MIDI Output Ports
- Arguments:
  - 0
    - Type: Int
    - Range: 0 to 127

# Messages Sent to Clients

## OSC Client Handling

### /client_registered
- Description: An OSC client has just been registered
- Arguments:
  - 0
    - Type: String
    - Description: Host name or IP address of client
  - 1
    - Type: Int
    - Description: Port that host is listening on

### /client_unregistered
- Description: An OSC client has just been unregistered
- Arguments:
  - 0
    - Type: String
    - Description: Host name or IP address of client
    - 1
      - Type: Int
      - Description: Port of client 

### /mod_wheel
- Description: A mod wheel MIDI Control Change Message (CC 1) has been received from a MIDI Input Port
- Arguments:
  - 0
    - Type: Int
    - Range: 0 to 127

### /aftertouch
- Description: A channel aftertouch MIDI message has been received from a MIDI Input Port
- Arguments:
  - 0
    - Type: Int
    - Range: 0 to 127

### /velocity
- Description: The velocity value of the most recently-received MIDI note-on message. nymphes_osc will output this message whenever a new note_on message is received. We only send this OSC message. We do not respond to incoming messages of this type.
- Arguments:
  - 0
    - Type: Int
    - Range: 0 to 127

## Preset Handling

### /loaded_preset
- Description: A program change message has just been received from the Nymphes, indicating that a preset was loaded from memory
- Arguments:
  - 0
    - Type: String
    - Description: Bank
      - Possible Values: 'A', 'B', 'C', 'D', 'E', 'F', 'G'
  - 1
    - Type: Int
    - Description: Preset Number
      - Possible Values: 1, 2, 3, 4, 5, 6, 7
  - 2
    - Type: String
    - Description: Type of preset
      - 'user' or 'factory'

### /loaded_preset_file
- Description: A preset file has just been loaded
- Arguments:
  - 0
    - Type: String
    - Description: Filepath of loaded preset

### /saved_preset_file
- Description: A preset file has just been saved
- Arguments:
  - 0
    - Type: String
    - Description: Filepath of saved preset

## MIDI Port Messages

### /nymphes_connected
- Description: The Nymphes synthesizer has just been connected
- Arguments: None

### /nymphes_disconnected
- Description: The Nymphes synthesizer has just been disconnected
- Arguments: None

### /midi_input_port_detected
- Description: A new non-Nymphes MIDI input port has been detected. This does not mean that we have connected to it.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the newly-detected MIDI input port 

### /midi_output_port_detected
- Description: A new non-Nymphes MIDI output port has been detected. This does not mean that we have connected to it.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the newly-detected MIDI output port 

### /midi_input_port_no_longer_detected
- Description: A previously-detected non-Nymphes MIDI input port is no longer detected.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the MIDI input port that is no longer detected 

### /midi_output_port_no_longer_detected
- Description: A previously-detected non-Nymphes MIDI output port is no longer detected.
- Arguments:
  - 0
    - Type: String
    - Description: The name of the MIDI output port that is no longer detected 

### /detected_midi_input_ports
- Description: A list of detected non-Nymphes MIDI input ports.
  - This is automatically sent to a newly-connected OSC host.
  - It is also sent to all OSC hosts whenever the list of input ports changes.
- Arguments: One String argument for the name of each detected input port
  - Note: If no input ports are detected, then the message will be sent but there will be no arguments

### /detected_midi_output_ports
- Description: A list of detected non-Nymphes MIDI output ports.
  - This is automatically sent to a newly-connected OSC host.
  - It is also sent to all OSC hosts whenever the list of output ports changes.
- Arguments: One String argument for the name of each detected output port
  - Note: If no output ports are detected, then the message will be sent but there will be no arguments

## Other Messages

### /status
- Description: A general status message. These messages mirror those output on the console of the machine running the nymphes_osc application
- Arguments:
  - 0
    - Type: String

### /nymphes_midi_channel_changed
- Description: The MIDI channel that Nymphes uses changed
- Arguments:
  - 0
    - Type: Int
    - Range: 1 to 16
    - Description: The MIDI channel
