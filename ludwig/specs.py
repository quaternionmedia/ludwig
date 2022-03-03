from pluggy import HookspecMarker
from rtmidi.midiutil import open_midioutput, open_midiinput
from rtmidi.midiconstants import CONTROL_CHANGE

mix = HookspecMarker('mixer')

class Mixer:
    @mix
    def mute(self, channel: int):
        '''mute channel'''
    @mix
    def unmute(self, channel: int):
        '''unmute channel'''
    @mix
    def fader(self, channel: int, volume: int):
        '''set the fader volume of a channel'''
    @mix
    def pan(self, channel: int, pan: int):
        '''set pan of the channel'''
    @mix
    def compressor(self,
        channel: int, 
        type: int | None = None,
        attack: int | None = None,
        release: int | None = None,
        knee: int | None = None,
        ratio: int | None = None,
        threshold: int | None = None,
        gain: int | None = None):
        '''set the compressor of the channel'''
    @mix
    def meters(self):
        '''get all meter values'''
    @mix
    def allCall(self):
        '''get full board status'''
    

class Midi:
    def __init__(self, *args, port, client_name='midi', channel=0, input_name=None, **kwargs):
        self.port = port
        self.client_name = client_name
        self.channel = channel
        self.midi, self.name = open_midioutput(port, client_name=client_name+'-output')
        self.input, self.input_name = open_midiinput(input_name if input_name else port, client_name=client_name+'-input')
        self.input.ignore_types(sysex=False)
        self.input.set_callback(self)
    
    def nrpn(self, channel, param, data1, data2):
        self.midi.send_message([CONTROL_CHANGE | self.channel, 0x63, channel])
        self.midi.send_message([CONTROL_CHANGE | self.channel, 0x62, param])
        self.midi.send_message([CONTROL_CHANGE | self.channel, 0x6, data1])
        self.midi.send_message([CONTROL_CHANGE | self.channel, 0x26, data2])
    
    def __call__(self, event, data=None):
        message, deltatime = event
        print(self.client_name, message, deltatime)
