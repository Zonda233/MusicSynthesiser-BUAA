import numpy as np

from Config import *

class Tone:
    def wave(self, velocity: float, duration: int, pitch: float):
        """ virtual """

class Tone_Piano(Tone):
    ampA3 = np.array([0.883, 0.613, 0.085, 0.233, 0.233, 0.054, 0.043, 0.013, 0.011, 0.008, 0.002, 0.001, 0.002, 0.001, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000])
    phaA3 = np.array([0.035, 1.712, 1.712, -0.166, 2.797, -0.490, 1.716, 0.945, -1.547, -1.836, -2.311, 1.874, -1.408, -1.860, 2.647, 1.500, 2.755, 2.168, 2.077, 2.283])
    decA3 = np.array([165000, 120000, 25000, 60000, 23000, 30000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000, 21000])

    ampA4 = np.array([0.789, 0.551, 0.058, 0.221, 0.245, 0.064, 0.199, 0.016, 0.101, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    phaA4 = np.array([0.806, -0.380, 1.254, -1.752, 2.697, -1.310, -0.032, -1.039, 1.152, -0.854, 2.135, -0.646, 0.482, 0.560, 1.278, 1.278, -0.377, -1.680, -1.680, -3.048])
    decA4 = np.array([92600, 90000, 66000, 86000, 57000, 30000, 24000, 24000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000])

    ampA5 = np.array([0.308, 0.253, 0.054, 0.005, 0.001, 0.001, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    phaA5 = np.array([-0.854, -0.631, 0.935, 0.935, 2.234, 2.234, 3.006, 3.006, 1.580, 1.580, -2.298, -2.298, -0.042, -0.042, 0.099, 0.099, 0.492, 0.492, 0.309, 0.309])
    decA5 = np.array([42000, 34000, 21000, 20000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000])

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

class Tone_Vibrate(Tone):
    def __init__(self,
                 arr_amplitude: np.array,
                 arr_phase: np.array,
                 vibrato_speed: float,
                 vibrato_amp: float):
        self.amp = arr_amplitude
        self.pha = arr_phase
        self.vib_spd = vibrato_speed
        self.vib_amp = vibrato_amp

    def wave(self, velocity: float, duration: int, pitch: int):
        out = np.zeros(duration)
        t = np.array(range(duration)).astype(np.float64)
        base = 2 * np.pi * float(pitch) / float(sr)
        for i in range(self.amp.size):
            wave = self.amp[i] * np.cos((i + 1) * base * t + self.pha[i])
            wave *= 1 + self.vib_amp * np.cos(self.vib_spd * t + self.pha[i])
            out += wave
        out = out * velocity
        return out

tone_violin = Tone_Vibrate(np.array([1.976, 0.159, 0.053, 0.095, 0.061, 0.040, 0.025, 0.061, 0.008, 0.021, 0.007, 0.005, 0.008, 0.003, 0.002, 0.003, 0.002, 0.001, 0.001, 0.001]),
                           np.array([-2.668, -1.857, 1.740, -1.102, 3.003, -0.211, -0.053, -0.143, -0.399, -1.253, 2.957, -2.237, -1.754, -1.392, -0.800, -1.351, 0.105, -0.907, -0.398, -1.601]),
                           5 * 2 * np.pi / sr, 0.15)

tone_flute = Tone_Vibrate(np.array([0.813, 0.489, 0.189, 0.228, 0.110, 0.025, 0.015, 0.009, 0.005, 0.005, 0.003, 0.001, 0.002, 0.001, 0.001]),
                          np.array([1.772, 0.379, 2.269, 1.275, 1.536, -2.139, -0.177, 1.028, 1.765, 2.090, 2.352, 1.728, 2.498, 0.801, 2.217]),
                          4 * 2 * np.pi / sr, 0.25)
tone_oboe = Tone_Vibrate(np.array([0.167, 0.379, 0.900, 0.108, 0.004, 0.064, 0.040, 0.005, 0.002, 0.009, 0.002, 0.002, 0.002, 0.001]),
                         np.array([2.699, -1.076, 2.569, 2.815, 1.399, -1.109, 2.317, 1.807, 0.226, 2.049, 0.659, 1.667, 1.820, 2.692]),
                         4 * 2 * np.pi / sr, 0.25)
tone_clarinet = Tone_Vibrate(np.array([0.818, 0.018, 0.511, 0.044, 0.242, 0.044, 0.077, 0.027, 0.007, 0.017]),
                             np.array([2.738, -1.314, -0.027, 0.276, -2.856, -2.542, 3.022, -1.805, 0.379, -1.729]),
                             4 * 2 * np.pi / sr, 0.25)
tone_bassoon = Tone_Vibrate(np.array([0.079, 0.061, 0.139, 0.686, 0.681, 0.077, 0.048, 0.079, 0.075, 0.056, 0.100, 0.017, 0.041, 0.025, 0.011, 0.007, 0.018, 0.013, 0.006, 0.006]),
                           np.array([-1.101, -2.556, -2.259, 2.080, 2.321, 0.171, -2.176, 1.527, -0.197, 0.595, 0.345, -1.666, 2.316, -0.075, -1.274, 2.391, 1.287, 1.563, 1.127, 1.127]),
                           4 * 2 * np.pi / sr, 0.25)
tone_horn = Tone_Vibrate(np.array([0.292, 0.793, 0.459, 0.164, 0.181, 0.054, 0.082, 0.069, 0.014, 0.013, 0.010, 0.009, 0.013, 0.015, 0.004, 0.002, 0.002, 0.003, 0.003, 0.002]),
                         np.array([2.829, 1.900, -0.697, 0.455, 1.765, -3.124, 1.265, 1.729, 1.626, 1.962, -2.402, -0.665, -0.830, -1.235, -2.579, -0.016, 0.251, 1.250, -0.689, 2.988]),
                         0.8 * 2 * np.pi / sr, 0.5)