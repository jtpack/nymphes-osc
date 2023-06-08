# Nymphes OSC Bridge

### A Software Object That Provides OSC Control of the Dreadbox Nymphes MIDI Synthesizer


# OSC and MIDI Message Reference

## Oscillator
- ### Oscillator Wave Shape
    - Value (CC# 70)
        - /osc/wave/value   
    - Modulation (CC# 31)
        - /osc/wave/mod/wheel
        - /osc/wave/mod/velocity
        - /osc/wave/mod/aftertouch
        - /osc/wave/mod/lfo2

- ### Oscillator Pulsewidth
    - Value (CC# 12)
        - /osc/pulsewidth/value   
    - Modulation (CC# 36)
        - /osc/pulsewidth/mod/wheel
        - /osc/pulsewidth/mod/velocity
        - /osc/pulsewidth/mod/aftertouch
        - /osc/pulsewidth/mod/lfo2

## Pitch
- ### Oscillator Detune
    - Value (CC# 15)
        - /pitch/detune/value   
    - Modulation (CC# 39)
        - /pitch/detune/mod/wheel
        - /pitch/detune/mod/velocity
        - /pitch/detune/mod/aftertouch
        - /pitch/detune/mod/lfo2

- ### Oscillator Chord Selector
    - Value (CC# 16)
        - /pitch/chord/value   
    - Modulation (CC# 40)
        - /pitch/chord/mod/wheel
        - /pitch/chord/mod/velocity
        - /pitch/chord/mod/aftertouch
        - /pitch/chord/mod/lfo2

- ### Pitch Envelope Depth
    - Value (CC# 14)
        - /pitch/env_depth/value   
    - Modulation (CC# 41)
        - /pitch/env_depth/mod/wheel
        - /pitch/env_depth/mod/velocity
        - /pitch/env_depth/mod/aftertouch
        - /pitch/env_depth/mod/lfo2

- ### Pitch LFO1 Depth
    - Value (CC# 13)
        - /pitch/lfo1/value   
    - Modulation (CC# 35)
        - /pitch/lfo1/mod/wheel
        - /pitch/lfo1/mod/velocity
        - /pitch/lfo1/mod/aftertouch
        - /pitch/lfo1/mod/lfo2

- ### Pitch Glide
    - Value (CC# 5)
        - /pitch/glide/value   
    - Modulation (CC# 37)
        - /pitch/glide/mod/wheel
        - /pitch/glide/mod/velocity
        - /pitch/glide/mod/aftertouch
        - /pitch/glide/mod/lfo2

## AMP

- ### Attack
    - Value (CC# 73)
        - /amp/attack/value   
    - Modulation (CC# 52)
        - /amp/attack/mod/wheel
        - /amp/attack/mod/velocity
        - /amp/attack/mod/aftertouch
        - /amp/attack/mod/lfo2

- ### Decay
    - Value (CC# 84)
        - /amp/decay/value   
    - Modulation (CC# 53)
        - /amp/decay/mod/wheel
        - /amp/decay/mod/velocity
        - /amp/decay/mod/aftertouch
        - /amp/decay/mod/lfo2

- ### Sustain
    - Value (CC# 85)
        - /amp/sustain/value   
    - Modulation (CC# 54)
        - /amp/sustain/mod/wheel
        - /amp/sustain/mod/velocity
        - /amp/sustain/mod/aftertouch
        - /amp/sustain/mod/lfo2

- ### Release
    - Value (CC# 72)
        - /amp/release/value   
    - Modulation (CC# 55)
        - /amp/release/mod/wheel
        - /amp/release/mod/velocity
        - /amp/release/mod/aftertouch
        - /amp/release/mod/lfo2

- ### Level (Master Volume)
    - CC# 7
    - /amp/level/value

## MIX

- ### Oscillator Level
    - Value (CC# 9)
        - /mix/osc/value   
    - Modulation (CC# 32)
        - /mix/osc/mod/wheel
        - /mix/osc/mod/velocity
        - /mix/osc/mod/aftertouch
        - /mix/osc/mod/lfo2

- ### Sub Level
    - Value (CC# 10)
        - /mix/sub/value   
    - Modulation (CC# 33)
        - /mix/sub/mod/wheel
        - /mix/sub/mod/velocity
        - /mix/sub/mod/aftertouch
        - /mix/sub/mod/lfo2

- ### Noise Level
    - Value (CC# 11)
        - /mix/noise/value   
    - Modulation (CC# 34)
        - /mix/noise/mod/wheel
        - /mix/noise/mod/velocity
        - /mix/noise/mod/aftertouch
        - /mix/noise/mod/lfo2


## LPF

- ### Cutoff
    - Value (CC# 74)
        - /lpf/cutoff/value   
    - Modulation (CC# 42)
        - /lpf/cutoff/mod/wheel
        - /lpf/cutoff/mod/velocity
        - /lpf/cutoff/mod/aftertouch
        - /lpf/cutoff/mod/lfo2

- ### Resonance
    - Value (CC# 71)
        - /lpf/resonance/value   
    - Modulation (CC# 43)
        - /lpf/resonance/mod/wheel
        - /lpf/resonance/mod/velocity
        - /lpf/resonance/mod/aftertouch
        - /lpf/resonance/mod/lfo2

- ### Tracking
    - Value (CC# 4)
        - /lpf/tracking/value   
    - Modulation (CC# 46)
        - /lpf/tracking/mod/wheel
        - /lpf/tracking/mod/velocity
        - /lpf/tracking/mod/aftertouch
        - /lpf/tracking/mod/lfo2

- ### Envelope Depth
    - Value (CC# 3)
        - /lpf/env_depth/value   
    - Modulation (CC# 44)
        - /lpf/env_depth/mod/wheel
        - /lpf/env_depth/mod/velocity
        - /lpf/env_depth/mod/aftertouch
        - /lpf/env_depth/mod/lfo2

- ### LFO1 Depth
    - Value (CC# 8)
        - /lpf/lfo1/value   
    - Modulation (CC# 47)
        - /lpf/lfo1/mod/wheel
        - /lpf/lfo1/mod/velocity
        - /lpf/lfo1/mod/aftertouch
        - /lpf/lfo1/mod/lfo2

## HPF

- ### Cutoff
    - Value (CC# 81)
        - /hpf/cutoff/value   
    - Modulation (CC# 45)
        - /hpf/cutoff/mod/wheel
        - /hpf/cutoff/mod/velocity
        - /hpf/cutoff/mod/aftertouch
        - /hpf/cutoff/mod/lfo2

## Pitch / Filter Envelope

- ### Attack
    - Value (CC# 79)
        - /pitch_filter_env/attack/value   
    - Modulation (CC# 48)
        - /pitch_filter_env/attack/mod/wheel
        - /pitch_filter_env/attack/mod/velocity
        - /pitch_filter_env/attack/mod/aftertouch
        - /pitch_filter_env/attack/mod/lfo2

- ### Decay
    - Value (CC# 80)
        - /pitch_filter_env/decay/value   
    - Modulation (CC# 49)
        - /pitch_filter_env/decay/mod/wheel
        - /pitch_filter_env/decay/mod/velocity
        - /pitch_filter_env/decay/mod/aftertouch
        - /pitch_filter_env/decay/mod/lfo2

- ### Sustain
    - Value (CC# 82)
        - /pitch_filter_env/sustain/value   
    - Modulation (CC# 50)
        - /pitch_filter_env/sustain/mod/wheel
        - /pitch_filter_env/sustain/mod/velocity
        - /pitch_filter_env/sustain/mod/aftertouch
        - /pitch_filter_env/sustain/mod/lfo2

- ### Release
    - Value (CC# 83)
        - /pitch_filter_env/release/value   
    - Modulation (CC# 51)
        - /pitch_filter_env/release/mod/wheel
        - /pitch_filter_env/release/mod/velocity
        - /pitch_filter_env/release/mod/aftertouch
        - /pitch_filter_env/release/mod/lfo2


## LFO1 (Filter / Pitch)

- ### Rate
    - Value (CC# 18)
        - /lfo1/rate/value   
    - Modulation (CC# 56)
        - /lfo1/rate/mod/wheel
        - /lfo1/rate/mod/velocity
        - /lfo1/rate/mod/aftertouch
        - /lfo1/rate/mod/lfo2

- ### Wave
    - Value (CC# 19)
        - /lfo1/wave/value   
    - Modulation (CC# 57)
        - /lfo1/wave/mod/wheel
        - /lfo1/wave/mod/velocity
        - /lfo1/wave/mod/aftertouch
        - /lfo1/wave/mod/lfo2

- ### Delay
    - Value (CC# 20)
        - /lfo1/delay/value   
    - Modulation (CC# 58)
        - /lfo1/delay/mod/wheel
        - /lfo1/delay/mod/velocity
        - /lfo1/delay/mod/aftertouch
        - /lfo1/delay/mod/lfo2

- ### Fade
    - Value (CC# 21)
        - /lfo1/fade/value   
    - Modulation (CC# 59)
        - /lfo1/fade/mod/wheel
        - /lfo1/fade/mod/velocity
        - /lfo1/fade/mod/aftertouch
        - /lfo1/fade/mod/lfo2

- ### Type
    - CC# 22
    - /lfo1/type/value
    - Possible Values:
        - 0: BPM
        - 1: Low
        - 2: High
        - 3: Track

- ### Key Sync
    - CC# 23
    - /lfo1/key_sync/value
    - Possible Values:
        - 0: Off
        - 1: On

## LFO2

- ### Rate
    - Value (CC# 24)
        - /lfo2/rate/value   
    - Modulation (CC# 60)
        - /lfo2/rate/mod/wheel
        - /lfo2/rate/mod/velocity
        - /lfo2/rate/mod/aftertouch
        - /lfo2/rate/mod/lfo2

- ### Wave
    - Value (CC# 25)
        - /lfo2/wave/value   
    - Modulation (CC# 61)
        - /lfo2/wave/mod/wheel
        - /lfo2/wave/mod/velocity
        - /lfo2/wave/mod/aftertouch
        - /lfo2/wave/mod/lfo2

- ### Delay
    - Value (CC# 26)
        - /lfo2/delay/value   
    - Modulation (CC# 62)
        - /lfo2/delay/mod/wheel
        - /lfo2/delay/mod/velocity
        - /lfo2/delay/mod/aftertouch
        - /lfo2/delay/mod/lfo2

- ### Fade
    - Value (CC# 27)
        - /lfo2/fade/value   
    - Modulation (CC# 63)
        - /lfo2/fade/mod/wheel
        - /lfo2/fade/mod/velocity
        - /lfo2/fade/mod/aftertouch
        - /lfo2/fade/mod/lfo2

- ### Type
    - CC# 28
    - /lfo2/type/value
    - Possible Values:
        - 0: BPM
        - 1: Low
        - 2: High
        - 3: Track

- ### Key Sync
    - CC# 29
    - /lfo2/key_sync/value
    - Possible Values:
        - 0: Off
        - 1: On

## Reverb

- ### Size
    - Value (CC# 75)
        - /reverb/size/value   
    - Modulation (CC# 86)
        - /reverb/size/mod/wheel
        - /reverb/size/mod/velocity
        - /reverb/size/mod/aftertouch
        - /reverb/size/mod/lfo2

- ### Decay
    - Value (CC# 76)
        - /reverb/decay/value   
    - Modulation (CC# 87)
        - /reverb/decay/mod/wheel
        - /reverb/decay/mod/velocity
        - /reverb/decay/mod/aftertouch
        - /reverb/decay/mod/lfo2

- ### Filter
    - Value (CC# 77)
        - /reverb/filter/value   
    - Modulation (CC# 88)
        - /reverb/filter/mod/wheel
        - /reverb/filter/mod/velocity
        - /reverb/filter/mod/aftertouch
        - /reverb/filter/mod/lfo2

- ### Mix
    - Value (CC# 78)
        - /reverb/mix/value   
    - Modulation (CC# 89)
        - /reverb/mix/mod/wheel
        - /reverb/mix/mod/velocity
        - /reverb/mix/mod/aftertouch
        - /reverb/mix/mod/lfo2

## Other Parameters
- ### Play Mode
    - CC# 17
    - /play_mode
    - Possible Values:
        - 0: Poly
        - 1: Uni-A (Six Voice)
        - 2: Uni-B (Four Voice)
        - 3: Tri
        - 4: Duo
        - 5: Mono

- ### Legato
    - CC# 68
    - /legato
    - Possible Values:
        - 0: Off
        - 1: On

- ### Mod Source Selector
    - CC# 30
    - /mod_source
    - Possible Values:
        - 0: LFO2
        - 1: Wheel
        - 2: Velocity
        - 3: Aftertouch
