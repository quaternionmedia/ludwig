from pluggy import HookspecMarker
from ludwig.types import uint3, uint7, uint8
from pydantic import conint

mix = HookspecMarker('mixer')


class Mixer:
    """A generic mixer class, to be overwritten by individual boards"""

    @mix
    def mute(self, channel: int):
        """mute channel"""

    @mix
    def unmute(self, channel: int):
        """unmute channel"""

    @mix
    def fader(self, channel: int, volume: int):
        """set the fader volume of a channel"""

    @mix
    def channel_assign_to_main_mix(self, channel: uint7, on: bool):
        """assign a channel to the main mix"""

    @mix
    def aux_send_level(self, channel: uint7, snd: uint8, level: uint8):
        """set the aux send level"""

    @mix
    def dca_assign(self, channel: uint7, dca: conint(ge=1, le=16), on: bool):
        """set the dca assignment for a channel"""

    @mix
    def channel_name(self, channel: uint7, name: str):
        """set the channel name. Must be less than 8 characters."""

    @mix
    def channel_color(self, channel: uint7, color: uint3):
        """set the channel color from 8 options:
        0: black
        1: red
        2: green
        3: yellow
        4: blue
        5: purple
        6: lt blue
        7: white
        """

    @mix
    def scene_recall(self, scene: conint(ge=1, le=500)):
        """recall scene, where scenes are 1 indexed"""
        self.send([0xB0 | self.channel, 0x0, scene // 128, scene % 128])

    @mix
    def mix_select(self, channel: uint7, select: bool):
        self.send([0xA0 | self.channel, channel, int(select)])

    @mix
    def pan(self, channel: int, pan: int):
        """set pan of the channel"""

    @mix
    def compressor(
        self,
        channel: int,
        type: int | None = None,
        attack: int | None = None,
        release: int | None = None,
        knee: int | None = None,
        ratio: int | None = None,
        threshold: int | None = None,
        gain: int | None = None,
    ):
        """set the compressor of the channel"""

    @mix
    def meters(self):
        """get all meter values"""

    @mix
    def allCall(self):
        """get full board status"""

    @mix
    def close(self):
        """close the midi connection"""
