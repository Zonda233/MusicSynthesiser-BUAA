import numpy as np
import wave
from Config import *
from Note import Note
from MIDIParser import *
from Enveloper import Enveloper
from Tone import Tone
from mido import MidiFile


Generate("拉赫玛尼诺夫第二钢琴协奏曲第一乐章钢琴.mid", "test.wav")
