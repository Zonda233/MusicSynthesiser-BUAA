from typing import Generator
from Note import Note
from mido import MidiFile

def Parser(filename: str) -> Generator[Note]:
    '''解析 MIDI 文件并生成音符的生成器'''
    midi = MidiFile(filename)
    current_time = 0  # 当前时间

    for msg in midi:
        current_time += msg.time  # 更新当前时间

        if msg.type == 'note_on':
            # 将音量参数标准化到 0 到 1 之间
            volume = msg.velocity / 127.0
            pitch = msg.note
            time = current_time
            # 计算时值（duration）和出现时间（time）在 44.1kHz 采样率下的数组长度和数组下标
            duration = int(msg.time * 44.1)  # 将时间转换为数组长度
            time_index = int(current_time * 44.1)  # 将时间转换为数组下标
            yield Note(volume=volume, pitch=pitch, duration=duration, time=time_index)