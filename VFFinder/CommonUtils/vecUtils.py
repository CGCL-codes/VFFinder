
import numpy as np


def cos_simialrity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
