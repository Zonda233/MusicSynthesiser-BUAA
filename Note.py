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

    def set_end(self, end_time):
        self.dura = end_time - self.pos

    def get_end(self) -> int:
        return self.pos + self.dura

    def wave(self) -> np.array:
        size = self.dura + self.env.R
        out = self.tone.wave(self.velo, size, self.pitch)

        env = np.zeros(size)
        if self.dura < self.env.A:
            env[0:self.dura] = np.linspace(0, 1, self.dura)
        elif self.dura < self.env.A + self.env.D:
            env[0:self.env.A] = np.linspace(0, 1, self.env.A)
            env[self.env.A:self.dura] = np.linspace(1, self.env.S, self.dura - self.env.A)
        else:
            env[0:self.env.A] = np.linspace(0, 1, self.env.A)
            env[self.env.A:self.env.A + self.env.D] = np.linspace(1, self.env.S, self.env.D)
            env[self.env.A + self.env.D:self.dura] = self.env.S

        env[self.dura:size] = np.linspace(self.env.S, 0, size - self.dura)
        out *= env

        return out
