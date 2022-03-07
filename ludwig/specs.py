from pluggy import HookspecMarker
from rtmidi.midiutil import open_midioutput, open_midiinput
from rtmidi.midiconstants import CONTROL_CHANGE
from ludwig.types import uint4, uint7, uint8, uint16

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


class Midi:
    def __init__(
        self,
        *args,
        port: str,
        client_name: str = 'midi',
        channel: uint4 = 0,
        input_name: str | None = None,
        **kwargs
    ):
        """A generic MIDI connection class
        attributes:
            port (str): the name of the MIDI port
            client_name (str): the name of the MIDI client to be connected
            channel (int): the MIDI channel to communicate on (default = 0)
            input_name (str): a custom name for the input client
        methods:
            send(message): send a MIDI message of bytes (sent as integers)
            nrpm(message): send a MIDI NRPN (Non-Registered Parameter Number)
        """

        self.port = port
        self.client_name = client_name
        self.channel = channel
        self.midi, self.name = open_midioutput(
            port, client_name=client_name + '-output'
        )
        self.input, self.input_name = open_midiinput(
            input_name if input_name else port, client_name=client_name + '-input'
        )
        self.input.ignore_types(sysex=False)
        self.input.set_callback(self)

    def send(self, message: list[uint8]):
        """send a regular MIDI message"""
        self.midi.send_message(message)

    def nrpn(self, channel: uint7, param: uint8, data1: uint8, data2: uint8):
        """send a MIDI Non-Registered Parameter Number"""
        header = CONTROL_CHANGE | self.channel
        self.send([header, 0x63, channel])
        self.send([header, 0x62, param])
        self.send([header, 0x6, data1])
        self.send([header, 0x26, data2])

    def __call__(self, event, data=None):
        message, deltatime = event
        print(self.client_name, message, deltatime)
