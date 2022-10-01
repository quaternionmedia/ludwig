from ludwig import mixer, Mixer, Midi
from rtmidi.midiconstants import NOTE_ON, CONTROL_CHANGE
from ludwig.types import uint1, uint2, uint3, uint4, uint5, uint7, uint8
from pydantic import conint


class XAir(Midi, Mixer):
    """Behringer XAir mixer"""

    @mixer
    def fader(self, channel: uint5, volume: uint7):
        """Fade the channel
        Fader       CH  CMD No.   Value    Comment
        CH Faders    1  CC  0-15   0...127  Input Channels 1-16
        CH Faders    1  CC  16     0...127  AuxLineIn 17-18 / USB Recorder Playback (stereo)
        CH Faders    1  CC  17-20  0...127  FX1-4 Return (stereo)
        Send Faders  1  CC  21-26  0...127  Aux1-6 / Subgroup
        Send Faders  1  CC  27-30  0...127  Fx1-4
        Main Fader   1  CC  31     0...127  Main LR (stereo)
        """
        self.send([CONTROL_CHANGE | 0, channel, volume])

    @mixer
    def pan(self, channel: uint5, pan: uint7):
        """Pan the channel
        Pan                 CH CMD No.    Value    Comment
        CH PAN              3  CC  0-15   1...127  Panorama Input Channels 1-16, 64=center
        CH PAN              3  CC  16     1...127  Balance AuxLineIn 17-18 / USB Recorder Playback, 64=center
        CH PAN              3  CC  17-20  1...127  Balance FX1-4 Return, 64=center
        Aux PAN (Subgroup)  3  CC  21-26  1...127  Panorama Aux1-6 / Subgroup, 64=center
        Main Balance        3  CC  31     1...127  Balance Main LR, 64=center
        """
        self.send([CONTROL_CHANGE | 2, channel, pan])

    @mixer
    def mute(self, channel: uint5):
        """Mute the channel
        Mute       CH CMD No.    Value   Comment
        CH Mutes   2  CC  0-15   0/127    Input Channels 1-16
        CH Mutes   2  CC  16     0/127    AuxLineIn 17-18 / USB Recorder Playback (stereo)
        CH Mutes   2  CC  17-20  0/127    FX1-4 Return (stereo)
        Send Mutes 2  CC  21-26  0/127    Aux1-6 / Subgroup
        Send Mutes 2  CC  27-30  0...127  Fx1-4
        Main Mute  2  CC  31     0/127    Main LR (stereo)
        """
        self.send([CONTROL_CHANGE | 1, channel, 127])

    @mixer
    def unmute(self, channel: uint7):
        """Mute the channel
        Mute       CH CMD No.    Value   Comment
        CH Mutes   2  CC  0-15   0/127    Input Channels 1-16
        CH Mutes   2  CC  16     0/127    AuxLineIn 17-18 / USB Recorder Playback (stereo)
        CH Mutes   2  CC  17-20  0/127    FX1-4 Return (stereo)
        Send Mutes 2  CC  21-26  0/127    Aux1-6 / Subgroup
        Send Mutes 2  CC  27-30  0...127  Fx1-4
        Main Mute  2  CC  31     0/127    Main LR (stereo)
        """
        self.send([CONTROL_CHANGE | 1, channel, 0])

