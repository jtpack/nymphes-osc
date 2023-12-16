# Nymphes OSC Bridge

### A software object that provides OSC control of the Dreadbox Nymphes MIDI synthesizer

# Nymphes Control OSC and MIDI Messages

## OSC Messages that nymphes-osc Accepts from Clients
- ### Set a Nymphes Preset Parameter with an Integer Value
- Address: /set_param_int
  - Description: Set a Nymphes parameter that is integer-valued, or a set a float parameter with a MIDI-style 0 to 127 integer.
  - Arguments:
    - 0
      - Type: String
      - Description: The name of the parameter. ie: 'main.lvl'
    - 1
      - Type: Int (Range: 0 to 127)
      - Description: The value

- Address: /set_param_float
  - Description: Set a Nymphes parameter that is float-valued. Do not try to set an integer parameter with this method.
  - Arguments:
    - 0
      - Type: String
      - Description: The name of the parameter. ie: 'main.lvl'
    - 1
      - Type: Float (Range: 0.0 to 1.0)
      - Description: The value

## OSC Messages that nymphes-osc Sends to Clients
- All notifications from nymphes-midi
  - The address will be the name of the notification
  - Arguments vary according to the notification

- ### Mod Wheel
  - CC# 1
  - /mod_wheel

- ### Velocity
  - Description: The velocity value of the most recently-received MIDI note-on message. nymphes_osc will output this message whenever a new note_on message is received. We only send this OSC message. We do not respond to incoming messages of this type.
  - /velocity

- ### Aftertouch
  - Description: The most recently-received channel aftertouch MIDI message (on the channel we are using for Nymphes)
  - /aftertouch

# Other OSC Messages

## Commands that nymphes_osc will accept

- ## Preset Handling

  - ### Load Preset from memory
    - Address: /load_preset
    - Arguments:
      - 0
        - Type: String
        - Description: Preset Bank 
        - Possible Values: 'A' through 'G'
      - 1
        - Type: Int
        - Description: Preset Number 
        - Possible Values: 1 through 7
      - 2
        - Type: String
        - Description: Preset Type
        - Possible Values: 'user' or 'factory'

  - ### Load a preset file from disk
    - Address: /load_preset_file
    - Arguments:
      - 0
        - Type: String
        - Description: Filepath of preset to load
      
  - ### Save current data to new preset file on disk
    - Address: /save_preset_file
    - Arguments:
      - 0
        - Type: String
        - Description: Filepath to save preset file to

- ## OSC Client Handling
  - ### Add an OSC Client
  - Address: /register_client
  - Arguments:
    - 0
      - Type: Int
      - Description: Port that host will be listening on
  - Notes:
    - The sender's IP address will be detected and used
      
    - Address: /register_client_with_ip_address
    - Arguments:
      - 0
        - Type: String
        - Description: Client name or IP address of host
      - 1
        - Type: Int
        - Description: Port that host will be listening on

  - ### Remove OSC Client
    - Address: /unregister_client
    - Arguments:
      - 0
        - Type: Int
        - Description: Client port
    - Notes:
      - The ip address of the sender will be used
    
    - Address: /unregister_client_with_ip_address
    - Arguments:
      - 0
        - Type: String
        - Description: Host name or IP address of client
      - 1
        - Type: Int
        - Description: Client port

  - ### Set Nymphes MIDI Channel
  - Description: Set the MIDI channel that Nymphes uses
  - Address: /set_nymphes_midi_channel
  - Arguments:
    - 0
      - Type: Int
      - Range: 1 to 16
      - Description: The MIDI channel

## Status messages that nymphes_osc can send

- ## Preset Handling

  - ### Nymphes Preset Loaded
    - Description: A program change message has just been received from the Nymphes,indicating that a preset was loaded from memory
    - Address: /loaded_preset
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

  - ### Preset file loaded
    - Description: A preset file has just been loaded
    - Address: /loaded_preset_file
    - Arguments:
      - 0
        - Type: String
        - Description: Filepath of loaded preset
      
  - ### Preset file saved
    - Description: A preset file has just been saved
    - Address: /saved_preset_file
    - Arguments:
      - 0
        - Type: String
        - Description: Filepath of saved preset

- ## OSC Client Handling
  - ### OSC Client Added
    - Description: An OSC client has just been added
    - Address: /client_registered
    - Arguments:
      - 0
        - Type: String
        - Description: Host name or IP address of client
      - 1
        - Type: Int
        - Description: Port that host is listening on

  - ### OSC Client Removed
    - Description: An OSC client has just been unregistered
    - Address: /client_unregistered
    - Arguments:
      - 0
        - Type: String
        - Description: Host name or IP address of client
      - 1
        - Type: Int
        - Description: Port of client 

- ## Miscellaneous Status Messages
  - ### General Status Update Message
    - Description: A general status message. These messages mirror those output on the console of the machine running the nymphes_osc application
    - Address: /status
    - Arguments:
      - 0
        - Type: String

  - ### Nymphes Connected
    - Description: The Nymphes synthesizer has just been connected
    - Address: /nymphes_connected
    - Arguments: None

  - ### Nymphes Disconnected
    - Description: The Nymphes synthesizer has just been disconnected
    - Address: /nymphes_disconnected
    - Arguments: None

  - ### New Non-Nymphes MIDI Input Port Detected
    - Description: A new non-Nymphes MIDI input port has been detected. This does not mean that we have connected to it.
    - Address: /midi_input_port_detected
    - Arguments:
      - 0
        - Type: String
        - Description: The name of the newly-detected MIDI input port 

  - ### New Non-Nymphes MIDI Output Port Detected
    - Description: A new non-Nymphes MIDI output port has been detected. This does not mean that we have connected to it.
    - Address: /midi_output_port_detected
    - Arguments:
      - 0
        - Type: String
        - Description: The name of the newly-detected MIDI output port 
  
  - ### MIDI Input Port No Longer Detected
    - Description: A previously-detected non-Nymphes MIDI input port is no longer detected.
    - Address: /midi_input_port_no_longer_detected
    - Arguments:
      - 0
        - Type: String
        - Description: The name of the MIDI input port that is no longer detected 

  - ### MIDI Output Port No Longer Detected
    - Description: A previously-detected non-Nymphes MIDI output port is no longer detected.
    - Address: /midi_output_port_no_longer_detected
    - Arguments:
      - 0
        - Type: String
        - Description: The name of the MIDI output port that is no longer detected 

  - ### Detected Non-Nymphes MIDI Input Ports
    - Description: A list of detected non-Nymphes MIDI input ports.
      - This is automatically sent to a newly-connected OSC host.
      - It is also sent to all OSC hosts whenever the list of input ports changes.
    - Address: /detected_midi_input_ports
    - Arguments: One String argument for the name of each detected input port
      - Note: If no input ports are detected, then the message will be sent but there will be no arguments
 
  - ### Detected Non-Nymphes MIDI Output Ports
    - Description: A list of detected non-Nymphes MIDI output ports.
      - This is automatically sent to a newly-connected OSC host.
      - It is also sent to all OSC hosts whenever the list of output ports changes.
    - Address: /detected_midi_output_ports
    - Arguments: One String argument for the name of each detected output port
      - Note: If no output ports are detected, then the message will be sent but there will be no arguments
  
- ### Nymphes MIDI Channel Changed
  - Description: The MIDI channel that Nymphes uses changed
  - Address: /nymphes_midi_channel_changed
  - Arguments:
    - 0
      - Type: Int
      - Range: 1 to 16
      - Description: The MIDI channel
