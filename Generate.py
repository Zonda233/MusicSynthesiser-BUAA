import sys

from Config import *
from typing import Generator
from Note import Note
from mido import MidiFile
from Tone import Tone
from Enveloper import Enveloper
import wave
from typing import List

tone_violin = Tone(np.array([25.990, 7.031, 1.519, 4.561, 1.807, 1.475, 0.808, 1.352, 0.853, 0.258]),
                   np.array([-2.637, 2.062, 0.666, 0.712, 1.692, -0.564, 0.964, -0.129, -0.670, 2.284]))
tone_piano = Tone(np.array([5.541, 3.168, 0.406, 1.549, 1.722, 0.449, 1.395, 0.111, 0.706, 0.126, 0.351, 0.117, 0.199, 0.048, 0.276, 0.276, 0.079, 0.084, 0.084, 0.041]),
                  np.array([0.806, -0.380, 1.254, -1.752, 2.697, -1.310, -0.032, -1.039, 1.152, -0.854, 2.135, -0.646, 0.482, 0.560, 1.278, 1.278, -0.377, -1.680, -1.680, -3.048]),
                  np.array([92600, 90000, 66000, 86000, 57000, 30000, 24000, 24000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000]))
env_common = Enveloper(200, 200, 0.5, 20000)
env_piano = Enveloper(0, 0, 1, 10000)

tone_preset = [tone_piano, tone_violin]
env_preset = [env_common, env_piano]

def generate(filename: str, output_filename: str):
    midi = MidiFile(filename)
    audio_len = int(midi.length * sr)
    out = np.zeros(audio_len)
    tpb = midi.ticks_per_beat
    channel_velo = [128] * 64
    channel_breath = [128] * 64
    convert = lambda x: int(x / (tpb * 1000000) * sr)

    total_msg_num = len(midi.merged_track)
    msg_cnt = 0
    track_cnt = 0

    # for track in midi.tracks:

    tempo = 0
    time_cur = int(0)  # 单位：1/tpb 微秒
    note_list: List[Note] = [[None] * 128 for _ in range(32)]  # 当前每个不同音高的音符列表
    tone = tone_preset[1]
    env = env_preset[0]
    pedal_on = False

    for msg in midi.merged_track:
        ticks = msg.time
        time_cur += ticks * tempo
        if not msg.is_meta:
            channel = msg.channel
            if msg.type == 'note_on':
                pitch = msg.note
                note_prev = note_list[channel][pitch]
                velo = msg.velocity * channel_velo[channel] * channel_breath[channel] / 128
                if note_prev is not None:
                    note_prev.set_end(convert(time_cur))
                    note_wave = note_prev.wave()
                    note_wave_size = note_wave.size
                    if note_prev.pos + note_wave_size > out.size:
                        out = np.append(out, np.zeros(note_prev.pos + note_wave_size - out.size + 10000))
                    out[note_prev.pos:note_prev.pos + note_wave.size] += note_wave
                    max_amp = max(out[note_prev.pos:note_prev.pos + note_wave.size])
                    if max_amp > 30000:
                        out[note_prev.pos:note_prev.pos + note_wave.size] *= 30000 / max_amp

                note_list[channel][pitch] = Note(convert(time_cur), velo, 0, frequencies[pitch] / 2, tone, env)

            if msg.type == 'control_change':
                if msg.control == 7:  # 通道音量
                    channel_velo[channel] = msg.value
                if msg.control == 2:  # 呼吸控制
                    channel_breath[channel] = msg.value
                if msg.control == 64:
                    """ 踏板控制，钢琴专用，待实现"""
        else:
            if msg.type == 'set_tempo':
                tempo = msg.tempo

        msg_cnt += 1
        print("\r", end="")
        print(f"Total Process: {msg_cnt: >7} / {total_msg_num: >7}, track {track_cnt: >3}", end="")
        sys.stdout.flush()

    track_cnt += 1

    testfile = wave.open(output_filename, 'w')
    testfile.setnchannels(1)
    testfile.setframerate(sr)
    testfile.setnframes(out.size)
    testfile.setsampwidth(2)
    testfile.writeframes(out.astype(np.int16))
