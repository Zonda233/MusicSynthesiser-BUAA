from typing import List
import numpy as np
import wave
from Config import *
from Note import Note
from Enveloper import Enveloper
from Tone import Tone
import Tone
from mido import MidiFile
from Generate import generate
import Generate
import mido

out = Note(0, 6000, 88200, 220, Tone.tone_viola, Generate.env_common).wave()
testfile = wave.open("files/test_viola.wav", 'w')
testfile.setnchannels(1)
testfile.setframerate(sr)
testfile.setnframes(out.size)
testfile.setsampwidth(2)
testfile.writeframes(out.astype(np.int16))