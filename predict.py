import pickle
from utils import *

return_deltadelta = True


def predict(gmm_path, wavefile, deltadelta: bool):
    """
    Predict whether the uploaded sound matches the speaker's model.
    :param gmm_path: Path to GMM pickle
    :param wavefile: Path to audio file
    :param deltadelta: Whether to use deltadelta or not
    :return: True if match, else False
    """
    gmm = pickle.load(open(gmm_path, 'rb'))  # Load GMM model
    feature = extract_features(wavefile, return_deltadelta=deltadelta)  # Extract features
    gmm_score = gmm.score(feature)  # Get GMM score of utterance
    print('GMM score: ' + str(gmm_score))

    if abs(gmm_score) <= 2.30:
        return True, gmm_score
    else:
        return False, gmm_score
