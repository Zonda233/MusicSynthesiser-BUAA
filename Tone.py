import numpy as np

class Tone:
    def __init__(self,
                 arr_amplitude: np.array,
                 arr_phase: np.array,
                 arr_decay_time=None):
        if arr_amplitude.size != arr_phase.size:
            raise ValueError("arr_amplitude and arr_phase should have the same size")
        velo = np.sqrt(np.sum(arr_amplitude ** 2))
        self.amp = arr_amplitude / velo
        self.pha = arr_phase.copy()
        self.dec = arr_decay_time
