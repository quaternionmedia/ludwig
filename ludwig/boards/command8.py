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

