from Config import *
from typing import Generator
from Note import Note
from mido import MidiFile
from Tone import Tone
from Enveloper import Enveloper
import wave

tone_violin = Tone(np.array([25.990, 7.031, 1.519, 4.561, 1.807, 1.475, 0.808, 1.352, 0.853, 0.258]),
                   np.array([-2.637, 2.062, 0.666, 0.712, 1.692, -0.564, 0.964, -0.129, -0.670, 2.284]))
tone_piano = Tone(np.array([5.541, 3.168, 0.406, 1.549, 1.722, 0.449, 1.395, 0.111, 0.706, 0.126, 0.351, 0.117, 0.199, 0.048, 0.276, 0.276, 0.079, 0.084, 0.084, 0.041]),
                  np.array([0.806, -0.380, 1.254, -1.752, 2.697, -1.310, -0.032, -1.039, 1.152, -0.854, 2.135, -0.646, 0.482, 0.560, 1.278, 1.278, -0.377, -1.680, -1.680, -3.048]),
                  np.array([92600, 90000, 66000, 86000, 57000, 30000, 24000, 24000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000]))
env_common = Enveloper(200, 200, 0.5, 20000)
env_piano = Enveloper(0, 0, 1, 20000)

def Parser(midi):
    '''解析 MIDI 文件并生成音符的生成器'''
    # 假设midi.merged_track已经是一个处理过的track，其中包含了所有轨道合并的信息
    track = midi.merged_track
    time = 0
    # 用一个字典来缓存音符的持续时间和音高，用于在音符抬起时生成正确的时长
    note_cache = {}
    for msg in track:
        if msg.type == 'note_on':
            # 当velocity为0时，代表音符抬起
            if msg.velocity == 0:
                # 如果音符已经在缓存中，说明这是一个已经按下的音符，现在抬起
                if msg.note in note_cache:
                    start_time, pitch, velo = note_cache[msg.note]
                    # 计算音符时长
                    duration = int(time - start_time)
                    # 生成音符对象，音量为0表示音符抬起
                    yield Note(int(sr * start_time / 720), velo, duration, pitch, tone_violin, env_common)
                    # 从缓存中移除该音符
                    del note_cache[msg.note]
            else:
                # 如果velocity不为0，说明是音符按下
                # 缓存音符的开始时间和音高
                note_cache[msg.note] = (time, frequencies[msg.note] / 2, msg.velocity)
        # 更新时间
        time += msg.time

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
