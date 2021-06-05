import numpy as np
from python_speech_features import mfcc
from scipy.io.wavfile import read
from sklearn import preprocessing


def calculate_delta(data, coeff):
    """
    Calculate and returns the delta of given feature vector matrix.
    :param data: Feature vector matrix
    :return: Delta of given input
    """
    rows, cols = data.shape
    deltas = np.zeros((rows, coeff))  # Shape: (rows, coeff)
    n = 2
    for i in range(rows):
        index = []
        j = 1
        while j <= n:
            if i - j < 0:
                first = 0
            else:
                first = i - j
            if i + j > rows - 1:
                second = rows - 1
            else:
                second = i + j
            index.append((second, first))
            j += 1
        deltas[i] = (data[index[0][0]] - data[index[0][1]] + (2 * (data[index[1][0]] - data[index[1][1]]))) / 10
    return deltas


def extract_features(audio_path, return_deltadelta: bool):
    """
    Extract 20-dim MFCC features from an audio, performs Cepstral Mean Subtraction
    and combines delta to make it 40-dim feature vector.
    :param audio_path: Path to audio file
    :param return_deltadelta: Should result feature vector include delta delta
    :return: 40-dim or 60-dim (if return_deltadelta is True) feature vector
    """
    sr, audio = read(audio_path)
    coeff = 13
    mfcc_feature = mfcc(audio, sr, 0.025, 0.01, coeff, nfft=1200, appendEnergy=True)
    mfcc_feature = preprocessing.scale(mfcc_feature)  # Cepstral Mean Subtraction
    delta = calculate_delta(mfcc_feature, coeff)
    if not return_deltadelta:
        combined = np.hstack((mfcc_feature, delta))
        return combined
    else:
        deltadelta = calculate_delta(delta, coeff)
        combined = np.hstack((mfcc_feature, delta, deltadelta))
        return combined