from Config import *

def get_wav(filename: str) -> np.ndarray:
    """读取.wav文件并返回numpy数组"""
    with wave.open(filename, 'rb') as wav_file:
        # 读取所有的帧
        _, sampwidth, _, nframes, _, _ = wav_file.getparams()
        frames = wav_file.readframes(nframes)
        # 将字符串转换为数值类型
        if sampwidth == 1:
            dtype = np.int8
        elif sampwidth == 2:
            dtype = np.int16
        elif sampwidth == 4:
            dtype = np.int32
        else:
            raise ValueError("Unsupported sample width")

        data = np.frombuffer(frames, dtype=dtype).astype(float)

        return data

class Tone:
    def wave(self, velocity: float, duration: int, pitch: float):
        """ virtual """

class Tone_Void(Tone):
    def wave(self, velocity: float, duration: int, pitch: float):
        out = np.zeros(duration)
        return out

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

class Tone_Flat(Tone):
    def __init__(self,
                 arr_amplitude: np.array,
                 arr_phase: np.array):
        self.amp = arr_amplitude
        self.pha = arr_phase

    def wave(self, velocity: float, duration: int, pitch: int):
        out = np.zeros(duration)
        t = np.array(range(duration)).astype(np.float64)
        base = 2 * np.pi * float(pitch) / float(sr)
        for i in range(self.amp.size):
            wave = self.amp[i] * np.cos((i + 1) * base * t + self.pha[i])
            out += wave
        out = out * velocity
        return out

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

# class Tone_Brass(Tone):
#

class Tone_Drum(Tone):
    def __init__(self, filename: str):
        self.waveform = get_wav(filename) / 2048

    def wave(self, velocity: float, duration: int, pitch: float):
        adjusted_waveform = self.waveform * velocity
        # 根据持续时间截断或补零
        if duration > len(adjusted_waveform):
            padding = np.zeros(duration - len(adjusted_waveform), dtype=adjusted_waveform.dtype)
            adjusted_waveform = np.concatenate((adjusted_waveform, padding))
        else:
            adjusted_waveform = adjusted_waveform[:duration]

        return adjusted_waveform

tone_void = Tone_Void
tone_sine = Tone_Flat(np.array([2]), np.array([0]))
tone_piano = Tone_Piano()
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
                         0.8 * 2 * np.pi / sr, 0.3)
tone_trumpet = Tone_Vibrate(np.array([0.424, 0.382, 0.398, 0.421, 0.457, 0.233, 0.139, 0.103, 0.145, 0.115, 0.082, 0.046, 0.032, 0.026, 0.021, 0.022, 0.015, 0.010, 0.009, 0.008]),
                            np.array([-2.077, -2.246, 0.436, 0.774, 0.911, 1.323, 1.099, -1.788, -1.556, -1.699, -1.729, 2.415, 0.924, 1.144, -0.485, 0.021, 0.372, 1.014, -1.870, -1.827]),
                            0.8 * 2 * np.pi / sr, 0.3)
tone_tuba = Tone_Flat(np.array([0.989, 0.144, 0.021, 0.003, 0.007, 0.004, 0.003, 0.003, 0.002, 0.002, 0.002, 0.002, 0.001, 0.002, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]),
                      np.array([0.690, 1.343, -0.911, -3.061, -0.809, -0.895, 2.971, -0.432, -0.274, -2.743, -2.838, 0.189, -2.291, -2.381, 0.826, 1.156, -1.908, -1.707, 1.525, -1.381]))
tone_violin = Tone_Vibrate(np.array([1.976, 0.159, 0.053, 0.095, 0.061, 0.040, 0.025, 0.061, 0.008, 0.021, 0.007, 0.005, 0.008, 0.003, 0.002, 0.003, 0.002, 0.001, 0.001, 0.001]),
                           np.array([-2.668, -1.857, 1.740, -1.102, 3.003, -0.211, -0.053, -0.143, -0.399, -1.253, 2.957, -2.237, -1.754, -1.392, -0.800, -1.351, 0.105, -0.907, -0.398, -1.601]),
                           5 * 2 * np.pi / sr, 0.15)
tone_viola = Tone_Vibrate(np.array([0.664, 0.398, 0.378, 0.157, 0.272, 0.138, 0.265, 0.107, 0.205, 0.116, 0.027, 0.020, 0.016, 0.023, 0.014, 0.025, 0.009, 0.011, 0.007, 0.005]),
                          np.array([1.799, -1.352, -0.986, -2.085, 1.099, 1.829, -0.142, -0.266, 1.099, -0.146, 0.458, 1.264, -1.788, 2.913, -0.580, -1.909, 1.260, -1.687, 2.821, -2.211]),
                          4 * 2 * np.pi / sr, 0.2)
tone_cello = tone_viola
tone_double_bass = Tone_Vibrate(np.array([0.963, 0.099, 0.108, 0.108, 0.101, 0.044, 0.092, 0.033, 0.062, 0.097, 0.012, 0.035, 0.018, 0.032, 0.031, 0.015, 0.010, 0.028, 0.014, 0.021]),
                                np.array([1.773, -2.026, -2.657, -1.470, -3.071, -1.633, -1.433, 1.249, -0.156, -1.585, -2.785, 1.969, 1.442, -0.782, 1.394, 1.386, 2.754, -2.749, -0.600, 1.420]),
                                2 * 2 * np.pi / sr, 0.2)
tone_drum = Tone_Drum("data/BassDrum.wav")
