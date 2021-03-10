from pluggy import HookspecMarker
from rtmidi.midiutil import open_midioutput, open_midiinput

mix = HookspecMarker('mixer')

class Mixer:

class Midi:
    def __init__(self, *args, port, client_name='midi', channel=0, **kwargs):
        self.port = port
        self.client_name = client_name
        self.channel = channel
        self.midi, self.name = open_midioutput(port, client_name=client_name+'-output')
        self.input, self.input_name = open_midiinput(port, client_name=client_name+'-input')
        self.input.set_callback(self)
    
    def nrpn(self, channnel, param, data1, data2):
        self.midi.send_message([CONTROL_CHANGE | self.channel, 0x63, channel])
        self.midi.send_message([CONTROL_CHANGE | self.channel, 0x62, param])
        self.midi.send_message([CONTROL_CHANGE | self.channel, 0x6, data1])
        self.midi.send_message([CONTROL_CHANGE | self.channel, 0x26, data2])
    
    def __call__(self, event, data=None):
        message, deltatime = event
        print(self.client_name, message)