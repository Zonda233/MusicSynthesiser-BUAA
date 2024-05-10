import numpy as np

class Tone:
    def __init__(self,
                 arr_amplitude: np.array,
                 arr_phase: np.array):
        if arr_amplitude.size != arr_phase.size:
            raise ValueError("arr_amplitude and arr_phase should have the same size")
        self.amp = arr_amplitude.copy()
        self.pha = arr_phase.copy()
