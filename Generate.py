import sys

from Config import *
from typing import Generator
from Note import Note
from mido import MidiFile
from Tone import Tone
import Tone
from Enveloper import Enveloper
import wave
from typing import List

env_common = Enveloper(5000, 200, 1, 5000)
env_piano = Enveloper(0, 0, 1, 10000)

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
    tempo = 0
    time_cur = int(0)  # 单位：1/tpb 微秒
    note_list: List[Note] = [[None] * 128 for _ in range(32)]  # 当前每个不同音高的音符列表
    tone = Tone.tone_piano
    env = env_preset[1]
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
        print(f"Total Process: {msg_cnt: >7} / {total_msg_num: >7}", end="")
        sys.stdout.flush()

    max_amp = max(np.abs(out[:]))
    out = out / max_amp * 30000
    # high_amp = np.abs(out) > 5000
    # out[high_amp] = np.sign(out[high_amp]) * (5000 + (np.abs(out[high_amp]) - 5000) / (max_amp - 5000) * 5000)

    testfile = wave.open(output_filename, 'w')
    testfile.setnchannels(1)
    testfile.setframerate(sr)
    testfile.setnframes(out.size)
    testfile.setsampwidth(2)
    testfile.writeframes(out.astype(np.int16))
