import os
import pickle
from utils import *
import sys
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

ids = ['17021311', '17021332', '17021357', '18021113']  # ID used for testing

for threshold in np.arange(start=1.00, stop=3.10, step=0.10):
    imposter_attempts = 0
    imposter_accepted = 0
    legit_attempts = 0
    legit_rejected = 0
    for gt_id in ids:
        gmm = None
        for f in os.listdir('GMM-deltadelta'):
            if gt_id in f:
                gmm = pickle.load(open(os.path.join('GMM-deltadelta', f), 'rb'))
        assert gmm is not None  # Make sure GMM loaded properly

        for root, _, files in os.walk('testset'):
            for file in files:
                is_imposter = True
                if gt_id in file:
                    is_imposter = False

                if is_imposter:
                    imposter_attempts += 1
                else:
                    legit_attempts += 1

                feature = extract_features(os.path.join(root, file), True)
                gmm_score = gmm.score(feature)

                if abs(gmm_score) <= threshold:
                    if is_imposter:
                        imposter_accepted += 1
                else:
                    if not is_imposter:
                        legit_rejected += 1
    print(str(threshold), str(imposter_accepted) + '/' + str(imposter_attempts), str(legit_rejected) + '/' + str(legit_attempts))

