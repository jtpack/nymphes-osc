- Added /mod_source to the README
  - NymphesOSC sends /mod_source when it receives MIDI CC #30 from Nymphes, but it wasn't documented
- Added exception handling when sending MIDI messages, as this seems to happen on Windows

## v0.2.7

- Fixed bug where MIDI Program Change messages above 97 were being accepted and then causing a crash
  - Now these are ignored.


## v0.2.6

- Fixed bug where unsaved changes flag was not being reset after saving to a preset slot


## v0.2.5-beta

- Fixed bug: After importing a sysex file, the last file was being loaded instead of the first


## v0.2.4-beta

- Fixed bug where only preset files with a lowercase file extension could be loaded
  - Now both .txt and .TXT file will be accepted
- Did the same for .syx and .SYX files


## v0.2.3-beta

- Fixed a bug that was causing LFO2 type and key sync to not be set when loading a preset file or when using fine mode
  - It was a typo
    - LFO1 was being set instead


## v0.2.2-beta

- Finally discovered the nature of a strange voice mode behavior that I first noticed a few months ago: When sending a preset to Nymphes via SYSEX, if the voice mode was set to 3 (TRI), we would actually hear three voices, which is wrong. And if voice mode was set to 4 (DUO), then we would hear two voices, which also is wrong.
  - Turns out the order of these two modes is reversed in the protobuf definition (preset_pb2.pyi)
    - In the protobuf definition, they refer to these modes as uni_3 and uni_2, which would be the same as DUO and TRI, respectively, not the other way around
  - Now we compensate for this when sending and receiving SYSEX, and everything behaves as it should


## v0.2.1-beta

- Created new preset file version (v2.0.0), which removes all rows that aren't actual preset parameters
  - We weren't doing anything with those rows anyways
  - I didn't want people to who edit those values to be frustrated when nothing happens


## v0.2.0-beta

- Fixed bug where /loaded_preset_dump_from_midi_input_port and /saved_preset_dump_from_midi_input_port_to_preset OSC messages were not being sent with the MIDI port name
- Added virtual MIDI ports on macOS so that DAWs can directly communicate via MIDI with nymphes-osc
- Added separate feedback suppression time for SYSEX messages, as they appear to sometimes be echoed back after a very long delay (many seconds) 


## v0.1.9-beta

- Added MIDI feedback suppression, to prevent feedback from connected MIDI outputs and inputs
  - When enabled (the default), MIDI inputs ignore any copies they receive of MIDI messages recently sent to connected MIDI outputs
    - By default, "recent" is defined as 0.1 seconds
- Added support for .syx files that contain more than one Nymphes preset (as separate SYSEX messages)
- Fixed bug that would cause Exception if a program change message is received from a MIDI input port without ever having received a bank MSB message to change the current preset type from None.
- Added reception of polyphonic aftertouch messages
- Fixed bug where MIDI CC messages with incorrect ranges for a Nymphes preset parameter would raise an Exception
- Fixed bug in legato MIDI CC handling (CC 68):
  - Nymphes uses MIDI CC value 127 to enable legato, but protobuf preset has it as bool, so its values are 0 or 1
  - Now we handle legato specially
- Updated version in pyproject.toml
  - Wasn't doing this before


## v0.1.8-beta

- Added support for loading .syx SYSEX files
- Added /error for sending error messages to clients, separate from status messages


## v0.1.7-beta

- Moved logs to ~/Library/Application Support/nymphes-osc on macOS


## v0.1.6-beta

- Discovered that chord semitone values can be negative
  - Adjusted range to -127 to 127
- Renamed chords to better match what is written in the Nymphes Manual. Now the seven normal chords are named 1 through 7, and the default chord is chord 0.
  - All old preset files are incompatible unless you rename the chords to match
- Turns out Nymphes actually sends a value of 127 when legato is enabled, not 1 as indicated in the Nymphes manual
  - Now we do the same


## v0.1.5-beta

- Bugfix: MSB and Program Change messages received on MIDI Input ports were not triggering /loaded_preset.


## v0.1.4-beta

- Now we receive aftertouch messages on all channels in order to facilitate MPE
  - This means that the /aftertouch OSC message sent out reflects the most recent channel aftertouch message received, regardless of channel.


## v0.1.3-beta

- Now a notification is generated when the Nymphes MIDI channel changes
- Added a nymphes_midi_channel_changed MidiConnectionEvent
