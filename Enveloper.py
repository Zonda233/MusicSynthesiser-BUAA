from Config import *

class Enveloper:
    def __init__(self,
                 attack: int,
                 decay: int,
                 sustain: float,
                 release: int):
        self.A = attack  # 单位：采样点
        self.D = decay  # 单位：采样点
        self.S = sustain  # 0-1之间，代表保持期间的音量与设置音量之比
        self.R = release  # 单位：采样点

env_violin = Enveloper(5000, 200, 1, 5000)
env_piano = Enveloper(0, 0, 1, 10000)
env_common = Enveloper(800, 300, 0.5, 3000)