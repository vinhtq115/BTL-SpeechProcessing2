import os
import pickle
from utils import *

FILE_TO_PREDICT = '17021332_mix.wav'
GMM_DIR = r'D:\ISO\XLTN-GMM'

gmms = []
speakers = []
for root, _, files in os.walk(GMM_DIR):
    for file in files:
        if '.gmm' in file:
            speaker = file.split('\\')[-1].split('.')[0]
            speakers.append(speaker)
            gmm = pickle.load(open(os.path.join(root, file), 'rb'))
            gmms.append(gmm)

feature = extract_features(FILE_TO_PREDICT)
score_of_individual_comparision = np.zeros(len(gmms))
for i in range(len(gmms)):
    gmm = gmms[i]  # checking with each model one by one
    scores = np.array(gmm.score(feature))
    score_of_individual_comparision[i] = scores.sum()
print(score_of_individual_comparision)
winner = np.argmax(score_of_individual_comparision)
print(winner, score_of_individual_comparision[winner])
print(29, score_of_individual_comparision[29])
speaker_detected = speakers[winner]
print(speaker_detected)
