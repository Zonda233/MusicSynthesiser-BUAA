from typing import List

import numpy as np
import wave
from Config import *
from Note import Note
from MIDIParser import *
from Enveloper import Enveloper
from Tone import Tone
from mido import MidiFile
from Generate import generate
import mido

generate("files/Genshin2.mid", "files/test2.wav")

# midi = MidiFile("东方红.mid")
# msg = midi.tracks[0][9]
# if not msg.is_meta:
#     print("yes")

# wave_piano = Note(0, 16384, 44100, 220, tone_piano, env_piano).wave()
#
# testfile = wave.open("test_piano.wav", 'w')
# testfile.setnchannels(1)
# testfile.setframerate(sr)
# testfile.setnframes(wave_piano.size)
# testfile.setsampwidth(2)
# testfile.writeframes(wave_piano.astype(np.int16))
