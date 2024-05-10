import numpy as np
from Tone import Tone
from Enveloper import Enveloper
class Note:
    def __init__(
            self, 
            velocity: np.float64, 
            time: int, 
            duration: int, 
            freqeuncy: int
        ) -> None:
        
        self.velocity = velocity
        self.time = time
        self.duration = duration
        self.frequency = freqeuncy

    def get_array(self, tone: Tone, enveloper: Enveloper) -> np.ndarray:
        '''返回这个音符在时域上的序列'''
        pass