from flask import Flask, request
import soundfile
import json
import re
import librosa
import os
import io
import tempfile
import filetype
from predict import predict

app = Flask(__name__)
return_deltadelta = True
GMM_dir = 'GMM-delta' if not return_deltadelta else 'GMM-deltadelta'  # Directory to GMM models
id_pattern = re.compile('^[0-9]{8}$')  # RegEx pattern to check ID


@app.route('/recognize', methods=['POST'])
def recognize():
    # Check if the POST request contains valid ID
    if request.form.get('id') is None or request.form.get('id') == '':
        resp = {
            'status': 1,
            'message': 'Missing id.'
        }
        return json.dumps(resp)
    s_id = request.form.get('id')
    if not id_pattern.match(s_id):
        resp = {
            'status': 2,
            'message': 'ID in wrong format.'
        }
        return json.dumps(resp)

    # Get GMM model matching ID
    gmm = ''
    for fname in os.listdir(GMM_dir):
        if fname.startswith(s_id):
            gmm = os.path.join(GMM_dir, fname)
            break
    if gmm == '':  # GMM for this ID does not exist (a.k.a. ID not recognized).
        resp = {
            'status': 3,
            'message': 'ID not recognized. Please contact the administrators if this is a mistake.'
        }
        return json.dumps(resp)

    # Check if the POST request has the file part
    if len(request.files) == 0:  # If 0 files were found, return error
        resp = {
            'status': 4,
            'message': 'No files were uploaded.'
        }
        return json.dumps(resp)
    elif len(request.files) != 1:  # More than 1 file were found, return error
        resp = {
            'status': 5,
            'message': 'Too many files were uploaded. Only 1 is accepted.'
        }
        return json.dumps(resp)

    # Check if valid audio file is uploaded
    uploaded_audio_file = request.files[next(iter(request.files))]
    bytes_io = io.BytesIO(uploaded_audio_file.stream.read())
    kind = filetype.guess(bytes_io)  # Guess filetype
    bytes_io.seek(0)
    if kind is None or kind.mime[:5] != 'audio':  # Cannot guess filetype
        resp = {
            'status': 6,
            'message': 'Uploaded file is not an audio file.'
        }
        return json.dumps(resp)

    # Read audio bytes, downsample to 16kHz and convert to mono, then save it to disk as WAVE file
    data, sr = soundfile.read(bytes_io)
    data_mono = librosa.to_mono(data)
    data_resampled = librosa.resample(data_mono, sr, 16000)
    filepath = tempfile.TemporaryFile(suffix='.wav')  # Create a temporary file to save uploaded one
    soundfile.write(filepath, data_resampled, 16000)
    filepath.seek(0)

    # Predict
    result = predict(gmm, filepath, return_deltadelta)
    filepath.close()  # Close and destroy temporary file

    if result:
        resp = {
            'status': 0,
            'recognized': 1,
            'message': 'User recognized.'
        }
        return json.dumps(resp)
    else:
        resp = {
            'status': 0,
            'recognized': 0,
            'message': 'User not recognized. Please try again.'
        }
        return json.dumps(resp)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
