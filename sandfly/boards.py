from sandfly import mixer
from sandfly.specs import Midi, Mixer
from rtmidi.midiconstants import NOTE_ON, CONTROL_CHANGE
from typing import Union

class Qu24(Midi, Mixer):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.header = [0xF0 , 0x0 , 0x0 , 0x1A , 0x50 , 0x11 , 0x1 , 0x0 , self.channel]

    @mixer
    def allCall(self):
        self.midi.send_message(self.header[:-1] + [0x7F] + [0x10, 0x0, 0xF7])
    
    @mixer
    def fader(self, channel:int, volume: int):
        print(self.client_name, 'setting channel volume', channel, volume)
        self.nrpn(channel=channel, param=0x17, data1=volume, data2=0x7)
    
    @mixer
    def pan(self, channel:int, pan: int):
        self.nrpn(channel, 0x16, pan, 0x7)
    
    @mixer
    def compressor(self,
            channel: int, 
            type: Union[int, None] = None,
            attack: Union[int, None] = None,
            release: Union[int, None] = None,
            knee: Union[int, None] = None,
            ratio: Union[int, None] = None,
            threshold: Union[int, None] = None,
            gain: Union[int, None] = None):
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
        
