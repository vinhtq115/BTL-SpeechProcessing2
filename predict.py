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

    if abs(gmm_score) <= 8.0:
        return True
    else:
        return False
    # if abs(gmm_score) <= 4.0000:
    #     return True
    # elif abs(gmm_score) >= 10.0000:
    #     return False
    #
    # # GMM score between 4 and 10
    # result = gmm.score_samples(feature)
    # avg = abs(gmm_score)
    # ress = {'lower': 0, 'upper': 0}
    # for i in result:
    #     if abs(i) <= avg:
    #         ress['lower'] += 1
    #     else:
    #         ress['upper'] += 1
    # print(ress)
    # if ress['lower'] > ress['upper']:
    #     return True
    # else:
    #     return False