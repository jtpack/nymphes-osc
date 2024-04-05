## v0.1.5-beta
- Bugfix: MSB and Program Change messages received on MIDI Input ports were not triggering /loaded_preset.


## v0.1.4-beta
- Now we receive aftertouch messages on all channels in order to facilitate MPE
  - This means that the /aftertouch OSC message sent out reflects the most recent channel aftertouch message received, regardless of channel.


## v0.1.3-beta
#### Bugfixes
  - Now a notification is generated when the Nymphes MIDI channel changes
  - Added a nymphes_midi_channel_changed MidiConnectionEvent
