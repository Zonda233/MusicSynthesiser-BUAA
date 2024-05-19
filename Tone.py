import numpy as np

from Config import *

class Tone:
    def wave(self, velocity: float, duration: int, pitch: int):
        """ virtual """

class Tone_Piano(Tone):
    amp = np.array([0.789, 0.451, 0.058, 0.221, 0.245, 0.064, 0.199, 0.016, 0.101, 0.018, 0.050, 0.017, 0.028, 0.007, 0.039, 0.039, 0.011, 0.012, 0.012, 0.006])
    pha = np.array([0.806, -0.380, 1.254, -1.752, 2.697, -1.310, -0.032, -1.039, 1.152, -0.854, 2.135, -0.646, 0.482, 0.560, 1.278, 1.278, -0.377, -1.680, -1.680, -3.048])
    dec = np.array([92600, 90000, 66000, 86000, 57000, 30000, 24000, 24000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000])

    def __init__(self):
        """nothing"""

    def wave(self, velocity: float, duration: int, pitch: int):
        out = np.zeros(duration)
        t = np.array(range(duration)).astype(np.float64)
        base = 2 * np.pi * float(pitch) / float(sr)
        for i in range(self.amp.size):
            wave = self.amp[i] * np.cos((i + 1) * base * t + self.pha[i])
            dec_time = min(self.dec[i], duration)
            env_t = np.linspace(1, 0, dec_time)
            wave[0:dec_time] *= env_t
            wave[dec_time:duration] = 0
            out += wave
        out = out * velocity
        return out

tone_piano = Tone_Piano()

class Tone_Violin(Tone):
    amp = np.array([1.976, 0.159, 0.053, 0.095, 0.061, 0.040, 0.025, 0.061, 0.008, 0.021, 0.007, 0.005, 0.008, 0.003, 0.002, 0.003, 0.002, 0.001, 0.001, 0.001])
    pha = np.array([-2.668, -1.857, 1.740, -1.102, 3.003, -0.211, -0.053, -0.143, -0.399, -1.253, 2.957, -2.237, -1.754, -1.392, -0.800, -1.351, 0.105, -0.907, -0.398, -1.601])
    vibrato_speed = 5 * 2 * np.pi / sr
    vibrato_amp = 0.15

    def wave(self, velocity: float, duration: int, pitch: int):
        out = np.zeros(duration)
        t = np.array(range(duration)).astype(np.float64)
        base = 2 * np.pi * float(pitch) / float(sr)
        for i in range(self.amp.size):
            wave = self.amp[i] * np.cos((i + 1) * base * t + self.pha[i])
            wave *= 1 + self.vibrato_amp * np.cos(self.vibrato_speed * t + self.pha[i])
            out += wave
        out = out * velocity
        return out

tone_violin = Tone_Violin()
