from sandfly import mixer
from sandfly.specs import Mixer

class Qu24(Mixer):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
    
    @mixer
    def setChannelVolume(channel:int, volume: int):
        print('setting channel volume', channel, volume)