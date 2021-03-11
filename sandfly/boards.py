from sandfly import mixer
from sandfly.specs import Midi, Mixer
from rtmidi.midiconstants import NOTE_ON, CONTROL_CHANGE

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
