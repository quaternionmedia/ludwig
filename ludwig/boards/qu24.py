from ludwig import mixer, Midi, Mixer
from rtmidi.midiconstants import NOTE_ON
from ludwig.types import uint1, uint2, uint7, uint8


class Qu24(Midi, Mixer):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.sysex_header = [0xF0, 0x0, 0x0, 0x1A, 0x50, 0x11, 0x1, 0x0, self.channel]

    @mixer
    def allCall(self):
        self.send(self.sysex_header[:-1] + [0x7F] + [0x10, 0x0, 0xF7])

    @mixer
    def meters(self):
        self.send(self.sysex_header + [0x12, 0x1, 0xF7])

    @mixer
    def fader(self, channel: uint7, volume: uint8):
        self.nrpn(channel=channel, param=0x17, data1=volume, data2=0x7)

    @mixer
    def pan(self, channel: uint7, pan: uint8):
        self.nrpn(channel, 0x16, pan, 0x7)

    @mixer
    def mute(self, channel: uint7):
        self.send([NOTE_ON | self.channel, channel, 127])

    @mixer
    def unmute(self, channel: uint7):
        self.send([NOTE_ON | self.channel, channel, 1])

    @mixer
    def compressor(
        self,
        channel: uint7,
        type: uint2 | None = None,
        attack: uint7 | None = None,
        release: uint7 | None = None,
        knee: uint1 | None = None,
        ratio: uint7 | None = None,
        threshold: uint7 | None = None,
        gain: uint7 | None = None,
    ):
        """send values to the compressor

        Reuqired arguments:
            channel (uint7): MIDI channel

        Optional arguments:
            type (uint2): 4 allowed types
            attack (uint7): 300us to 300ms
            release (uint7): 100ms to 2s
            knee (uint1): 0 = hard, 1 = soft
            ratio (uint7): 1:1 to inf (e.g. 2.6:1 = 80)
            threshold (uint7): -46 to +18dB
            gain (uint7): 0 +18dB
        """

        if type:
            self.nrpn(channel, 0x61, type, 0x7)
        if attack:
            self.nrpn(channel, 0x62, attack, 0x7)
        if release:
            self.nrpn(channel, 0x63, release, 0x7)
        if knee:
            self.nrpn(channel, 0x64, knee, 0x7)
        if ratio:
            self.nrpn(channel, 0x65, ratio, 0x7)
        if threshold:
            self.nrpn(channel, 0x66, threshold, 0x7)

        if gain:
            self.nrpn(channel, 0x67, gain, 0x7)
