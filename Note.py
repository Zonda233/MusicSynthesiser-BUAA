import numpy as np
from Config import *
from Tone import Tone
from Enveloper import Enveloper

class Note:
    def __init__(self,
                 position: int,
                 velocity: float,
                 duration: int,
                 pitch: int,
                 tone: Tone,
                 enveloper: Enveloper):
        self.pos = position  # 位置 单位：采样点
        self.velo = velocity  # 音量
        self.dura = duration  # 时长 单位：采样点
        self.pitch = pitch  # 音高 单位：Hz
        self.tone = tone  # 音色 Tone对象
        self.env = enveloper  # 包络 Enveloper对象

    def wave(self) -> np.array:
        size = self.dura + self.env.R
        out = np.zeros(size)
        base = 2 * pi * float(self.pitch) / float(sr)
        t = np.array(range(size)).astype(np.float64)

        # 根据tone中的各个谐波的振幅、相位信息，生成初始波形
        for i in range(self.tone.amp.size):
            amp = self.tone.amp[i]
            pha = self.tone.pha[i]
            out += amp * np.cos((i + 1) * base * t + pha)
        out = out * self.velo

        # 对波形进行包络
        for i in range(self.dura):
            if i < self.env.A:
                out[i] *= i / self.env.A
            elif i < self.env.A + self.env.D:
                out[i] *= 1 + (self.env.S - 1) * (i - self.env.A) / self.env.D
            else:
                out[i] *= self.env.S
        for i in range(self.dura, size):
            out[i] *= (self.dura + self.env.R - i) * self.env.S / self.env.R

        return out
