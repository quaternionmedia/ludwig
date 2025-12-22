from ludwig import mixer, Mixer, Midi
from rtmidi.midiconstants import NOTE_ON, CONTROL_CHANGE
from ludwig.types import uint1, uint2, uint3, uint4, uint5, uint7, uint8


class Command8(Midi, Mixer):
    """Focusrite Command8 mixing station"""

    @mixer
    def fader(self, channel: uint4, volume: uint7):
        """Fade the channel"""
        self.send([CONTROL_CHANGE | channel, 7, volume])

    @mixer
    def pan(self, channel: uint4, pan: uint7):
        """Pan the channel"""
        self.send([CONTROL_CHANGE | channel, 10, pan])

    @mixer
    def mute(self, channel: uint4):
        """Mute the channel"""
        self.send([CONTROL_CHANGE | channel, 14, 127])

    @mixer
    def unmute(self, channel: uint4):
        """Unmute the channel"""
        self.send([CONTROL_CHANGE | channel, 14, 0])

    def __call__(self, event, data=None):
        message, deltatime = event
        print('Command8!', message, deltatime)
        if message[0] & 0xF0 == CONTROL_CHANGE:
            print(
                f'found control change message {message[0]} on channel {message[0] & 0x0F}'
            )
            if message[1] == 7:
                print(f'fader channel {message[0] & 0x0F } at {message[2]}')
                self.hook.fader(channel=message[0] & 0x0F, volume=message[2])
            elif message[1] == 10:
                print(f'pan channel {message[0] & 0x0F } at {message[2]}')
                self.hook.pan(channel=message[0] & 0x0F, pan=message[2])
            elif message[1] == 14:
                print(
                    f'{"un" if message[2] == 0 else ""}mute channel {message[0] & 0x0F }'
                )
                if message[2]:
                    self.hook.mute(channel=message[0] & 0x0F)
                else:
                    self.hook.unmute(channel=message[0] & 0x0F)
