"""Ludwig

Remote control mixing

Ludwig offers a pluggable interface to control mixing software in realtime.

It can run as a standalone server, or through a command line interface.
"""

from pluggy import HookimplMarker

from .mixer import Mixer
from .midi import Midi, MidiInput

mixer = HookimplMarker('mixer')
