import numpy as np

class Tone:
    def __init__(self,
                 arr_amplitude: np.array,
                 arr_phase: np.array):
        if arr_amplitude.size != arr_phase.size:
            raise ValueError("arr_amplitude and arr_phase should have the same size")
        velo = np.sqrt(np.sum(arr_amplitude ** 2))
        self.amp = arr_amplitude / velo * 8
        self.pha = arr_phase.copy()
