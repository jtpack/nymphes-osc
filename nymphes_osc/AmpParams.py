from ModulatedControlParameter import ModulatedControlParameter


class AmpParams:
    """A class for tracking all of amplitude-related control parameters"""

    def __init__(self, dispatcher, osc_client):
        self._attack = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/amp/attack')
        self._decay = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/amp/decay')
        self._sustain = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/amp/sustain')
        self._release = ModulatedControlParameter(dispatcher, osc_send_function, midi_send_function, '/amp/release')
        self._level = BasicControlParameter(dispatcher, osc_client, '/amp/level/value', min_val=0, max_val=127)

    @property
    def attack(self):
        return self._attack

    @property
    def decay(self):
        return self._decay

    @property
    def sustain(self):
        return self._sustain

    @property
    def release(self):
        return self._release

    @property
    def level(self):
        return self._level

