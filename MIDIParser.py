from typing import Generator
import numpy as np
from Note import Note

def Parser(filename: str) -> Generator[Note]:
    '''你的函数注释'''
    yield Note(0, 0, 0, 0)