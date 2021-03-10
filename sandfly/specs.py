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
    
    @mix
    def setChannelVolume(channel: int, volume: int):
        '''set the volume of given channel'''
    
    def __call__(self, event, data=None):
        message, deltatime = event
        print(self.client_name, message)
