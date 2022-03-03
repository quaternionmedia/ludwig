from ludwig import mixer
from ludwig.specs import Midi, Mixer
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, CONTROL_CHANGE
from pydantic import conint
from datetime import datetime

class Qu24(Midi, Mixer):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.header = [0xF0 , 0x0 , 0x0 , 0x1A , 0x50 , 0x11 , 0x1 , 0x0 , self.channel]
        self.start_time = datetime.now()
        self.log = []

    @mixer
    def allCall(self):
        self.send(self.header[:-1] + [0x7F] + [0x10, 0x0, 0xF7])
    
    @mixer
    def meters(self):
        self.send(self.header + [0x12, 0x1, 0xF7])
    
    @mixer
    def fader(self, channel:int, volume: int):
        print(self.client_name, 'setting channel volume', channel, volume)
        self.nrpn(channel=channel, param=0x17, data1=volume, data2=0x7)
    
    @mixer
    def pan(self, channel:int, pan: int):
        self.nrpn(channel, 0x16, pan, 0x7)
    
    @mixer
    def mute(self, channel:conint(ge=0, le=127)):
        self.send([NOTE_ON | self.channel, channel, 127])
    
    @mixer
    def unmute(self, channel:conint(ge=0, le=127)):
        self.send([NOTE_ON | self.channel, channel, 1])
    
    @mixer
    def compressor(self,
            channel: int, 
            type: int | None = None,
            attack: int | None = None,
            release: int | None = None,
            knee: int | None = None,
            ratio: int | None = None,
            threshold: int | None = None,
            gain: int | None = None):
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
    
    @mixer
    def close(self):
        from json import dump
        from os.path import join
        with open(join('logs', str(self.start_time) + '.json'), 'w') as f:
            dump(self.log, f)
    
    def __call__(self, event, data=None):
        super().__call__(event, data)
        self.log.append(event)
