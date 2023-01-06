from rtmidi.midiutil import open_midioutput, open_midiinput
from rtmidi.midiconstants import CONTROL_CHANGE
from ludwig.types import uint4, uint7, uint8
from rtmidi import API_UNIX_JACK


class Midi:
    def __init__(
        self,
        *args,
        hook,
        port: str,
        client_name: str = 'midi',
        channel: uint4 = 0,
        input_name: str | None = None,
        **kwargs,
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
        self.hook = hook
        self.port = port
        self.client_name = client_name
        self.channel = channel
        self.midi, self.name = open_midioutput(
            port, client_name=client_name + '-output', api=API_UNIX_JACK
        )
        self.input, self.input_name = open_midiinput(
            input_name if input_name else port,
            client_name=client_name + '-input',
            api=API_UNIX_JACK,
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

    def sysex(self, message: list[uint8]):
        """send a MIDI sysex message. Requires self.sysex_header to be set."""
        self.midi.send_message([*self.sysex_header, *message, 0xF7])

    def __call__(self, event, data=None):
        message, deltatime = event
        print(self.client_name, message, deltatime)


class MidiInput:
    def __init__(self, client_name='MidiInput', *args, **kwargs) -> None:
        self.name = client_name
        self.input, self.port_name = open_midiinput(
            None, api=1, use_virtual=True, client_name=client_name
        )
        print('connected', client_name)
        self.input.set_callback(self)
