import numpy as np

from Config import *

class Tone:
    def wave(self, velocity: float, duration: int, pitch: float):
        """ virtual """

class Tone_Piano(Tone):
    ampA3 = np.array([1.283, 0.513, 0.313, 0.133, 0.063, 0.024, 0.043, 0.013, 0.011, 0.008, 0.002, 0.001, 0.002, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000])
    phaA3 = np.array([0.035, 1.712, 1.712, -0.166, 2.797, -0.490, 1.716, 0.945, -1.547, -1.836, -2.311, 1.874, -1.408, -1.860, 2.647, 1.500, 2.755, 2.168, 2.077, 2.283])
    decA3 = np.array([165000, 23000, 91000, 36000, 33000, 30000, 43000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000])

    ampA4 = np.array([0.789, 0.451, 0.058, 0.221, 0.245, 0.064, 0.199, 0.016, 0.101, 0.018, 0.050, 0.017, 0.028, 0.007, 0.039, 0.039, 0.011, 0.012, 0.012, 0.006])
    phaA4 = np.array([0.806, -0.380, 1.254, -1.752, 2.697, -1.310, -0.032, -1.039, 1.152, -0.854, 2.135, -0.646, 0.482, 0.560, 1.278, 1.278, -0.377, -1.680, -1.680, -3.048])
    decA4 = np.array([92600, 90000, 66000, 86000, 57000, 30000, 24000, 24000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000])

    ampA5 = np.array([0.308, 0.053, 0.470, 0.470, 0.157, 0.157, 0.039, 0.039, 0.019, 0.019, 0.011, 0.011, 0.009, 0.009, 0.009, 0.009, 0.003, 0.003, 0.001, 0.001])
    phaA5 = np.array([-0.854, -0.631, 0.935, 0.935, 2.234, 2.234, 3.006, 3.006, 1.580, 1.580, -2.298, -2.298, -0.042, -0.042, 0.099, 0.099, 0.492, 0.492, 0.309, 0.309])
    decA5 = np.array([21000, 34000, 21000, 19000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000])

    def _interpolate_values(self, value1, value2, pitch1, pitch2, current_pitch):
        return value1 + (value2 - value1) * (current_pitch - pitch1) / (pitch2 - pitch1)

    def wave(self, velocity: float, duration: int, pitch: int):
     #   global ampA3, phaA3, decA3, ampA4, phaA4, decA4, ampA5, phaA5, decA5
        out = np.zeros(duration)
        t = np.array(range(duration)).astype(np.float64)
        pitchA3 = 220
        pitchA4 = 440
        pitchA5 = 880
        if pitch < pitchA3:
            # 如果频率低于最低点，使用最低点的值
            (self.amp, self.pha, self.dec) = (self.ampA3, self.phaA3, self.decA3)
        elif pitch < pitchA4:
            # 在A3和A4之间插值
            self.amp = self._interpolate_values(self.ampA3, self.ampA4, pitchA3, pitchA4, pitch)
            self.pha = self._interpolate_values(self.phaA3, self.phaA4, pitchA3, pitchA4, pitch)
            self.dec = self._interpolate_values(self.decA3, self.decA4, pitchA3, pitchA4, pitch).astype(np.int32)
        elif pitch < pitchA5:
            # 在A4和A5之间插值
            self.amp = self._interpolate_values(self.ampA4, self.ampA5, pitchA4, pitchA5, pitch)
            self.pha = self._interpolate_values(self.phaA4, self.phaA5, pitchA4, pitchA5, pitch)
            self.dec = self._interpolate_values(self.decA4, self.decA5, pitchA4, pitchA5, pitch).astype(np.int32)
        else:
            # 如果频率高于最高点，使用最高点的值
            (self.amp, self.pha, self.dec) = (self.ampA5, self.phaA5, self.decA5)
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
