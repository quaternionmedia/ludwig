from pluggy import HookspecMarker
from rtmidi.midiutil import open_midioutput, open_midiinput

mix = HookspecMarker('mixer')

class Mixer:
    def __init__(self, *args, hook, port, client_name='mixer', **kwargs):
        self.hook = hook
        self.port = port
        self.client_name = client_name
        self.midi, self.name = open_midioutput(port, client_name=client_name+'-output')
        self.input, self.input_name = open_midiinput(port, client_name=client_name+'-input')
        self.input.set_callback(self)
        return
    
    @mix
    def setChannelVolume(channel: int, volume: int):
        '''set the volume of given channel'''
    
    def __call__(self, event, data=None):
        message, deltatime = event
        print(self.client_name, message)
