from Config import *
from typing import Generator
from Note import Note
from mido import MidiFile
from Tone import Tone
from Enveloper import Enveloper
import wave

tone_violin = Tone(np.array([25.990, 7.031, 1.519, 4.561, 1.807, 1.475, 0.808, 1.352, 0.853, 0.258]),
                   np.array([-2.637, 2.062, 0.666, 0.712, 1.692, -0.564, 0.964, -0.129, -0.670, 2.284]))
common_env = Enveloper(500, 200, 1, 20000)

def Parser(midi):
    '''解析 MIDI 文件并生成音符的生成器'''
    # for track in midi.tracks:
    track = midi.merged_track
    time = 0
    for msg in track:
        if msg.type == 'note_on':
            dura = msg.time
            velo = msg.velocity
            note = msg.note
            yield Note(int(time * sr / 1000), float(velo), 700, frequencies[note] / 2, tone_violin, common_env)
            time += dura

def Generate(filename: str, output_filename: str):
    midi = MidiFile(filename)
    audio_len = int(midi.length * sr)
    out = np.zeros(audio_len)
    for note in Parser(midi):
        start = note.pos
        note_wave = note.wave()
        for i in range(note_wave.size):
            if start + i >= out.size:
                out = np.append(out, np.zeros(start + i - out.size + 100000))
            out[start + i] += note_wave[i]

    testfile = wave.open(output_filename, 'w')
    testfile.setnchannels(1)
    testfile.setframerate(sr)
    testfile.setnframes(out.size)
    testfile.setsampwidth(2)
    testfile.writeframes(out.astype(np.int16))
