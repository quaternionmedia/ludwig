from ludwig import mixer, Mixer, MidiInput
from rtmidi.midiconstants import NOTE_ON, CONTROL_CHANGE


class Hook:
    def __init__(self, hook, *args, **kwargs) -> None:
        self.hook = hook
        super().__init__(*args, **kwargs)


class Generic(Hook, MidiInput):
    def __call__(self, event, data=None):
        message, deltatime = event
        print('CC', message)
        if message[0] == CONTROL_CHANGE:
            cc = message[1]
            value = message[2]
            self.hook.fader(channerl=cc, volume=value)
