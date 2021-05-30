import os
import pickle
from sklearn.mixture import GaussianMixture
from tqdm import tqdm
from utils import *

DATASET_TRAIN_PATH = r'D:\ISO\XLTN-dataset'
SAVE_PATH = r'GMM-deltadelta'


def train_gmm(speaker_dir):
    # Get speaker's info
    speaker = speaker_dir.split('\\')[-1]
    print(speaker)

    stacked_feature = np.asarray(())  # For storing features

    # Get audio files
    wav_files = []
    for root, _, files in os.walk(speaker_dir):
        wav_files = [os.path.join(root, file) for file in files if '.wav' in file]

    print('Extracting features...')
    for file in tqdm(wav_files):
        current_audio_feature = extract_features(file, return_deltadelta=False)
        if stacked_feature.size == 0:
            stacked_feature = current_audio_feature
        else:
            stacked_feature = np.vstack((stacked_feature, current_audio_feature))

    print('Training GMM model...')
    gmm = GaussianMixture(n_components=16, covariance_type='diag', max_iter=500, n_init=3, verbose=1)
    gmm.fit(stacked_feature)  # Generate the GMM model of the stacked features

    print('Training complete. Dumping to disk...')
    pickle.dump(gmm, open(os.path.join(SAVE_PATH, speaker + '.gmm'), 'wb'))


for root, _, files in os.walk(DATASET_TRAIN_PATH):
    if len(files) == 0:
        continue  # Skip root folder

    # Train gmm for each speaker
    train_gmm(root)

