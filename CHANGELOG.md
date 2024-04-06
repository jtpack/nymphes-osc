
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
#### Bugfixes
  - Now a notification is generated when the Nymphes MIDI channel changes
  - Added a nymphes_midi_channel_changed MidiConnectionEvent
