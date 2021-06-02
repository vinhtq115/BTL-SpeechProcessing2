from flask import Flask, request, jsonify, render_template
import soundfile
import re
import librosa
import os
import io
import tempfile
import filetype
import mimetypes
from database import *
from predict import predict

app = Flask(__name__, template_folder='templates')
return_deltadelta = True
GMM_dir = 'GMM-delta' if not return_deltadelta else 'GMM-deltadelta'  # Directory to GMM models
id_pattern = re.compile('^[0-9]{8}$')  # RegEx pattern to check ID

mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/javascript', '.js')


@app.route('/recognize_api', methods=['POST'])
def recognize():
    # Check if the POST request contains valid ID
    if request.form.get('id') is None or request.form.get('id') == '':
        resp = {
            'status': 1,
            'message': 'Missing id.'
        }
        return jsonify(resp)
    s_id = request.form.get('id')
    if not id_pattern.match(s_id):
        resp = {
            'status': 2,
            'message': 'ID in wrong format.'
        }
        return jsonify(resp)

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
        return jsonify(resp)

    # Check if the POST request has the file part
    if len(request.files) == 0:  # If 0 files were found, return error
        resp = {
            'status': 4,
            'message': 'No files were uploaded.'
        }
        return jsonify(resp)
    elif len(request.files) != 1:  # More than 1 file were found, return error
        resp = {
            'status': 5,
            'message': 'Too many files were uploaded. Only 1 is accepted.'
        }
        return jsonify(resp)

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
        return jsonify(resp)

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

    if result:  # Speaker recognized
        is_new_shift, recorded_date = update_shift(s_id)
        s_name = get_name(s_id)
        resp = {
            'status': 0,
            'recognized': 1,
            'message': 'Employee {0} '.format(s_name) +
                       ('begins a new shift at {0}'.format(recorded_date) if is_new_shift
                        else 'ends current shift at {0}'.format(recorded_date))
        }
        return jsonify(resp)
    else:  # Speaker unrecognized.
        resp = {
            'status': 0,
            'recognized': 0,
            'message': 'User not recognized. Please try again.'
        }
        return jsonify(resp)


@app.route('/list_shift_api', methods=['GET'])
def list_shift():
    # Check ID
    s_id = request.args.get('id', default=None)
    if s_id is None:  # Missing id
        resp = {
            'status': 1,
            'message': 'Missing id.'
        }
        return jsonify(resp)
    if not id_pattern.match(s_id):  # Check if ID is in correct format
        resp = {
            'status': 2,
            'message': 'ID in wrong format.'
        }
        return jsonify(resp)

    # Check if ID exists
    id_exists = False
    for fname in os.listdir(GMM_dir):
        if fname.startswith(s_id):
            id_exists = True
            break
    if not id_exists:  # ID not recognized.
        resp = {
            'status': 3,
            'message': 'ID not recognized. Please contact the administrators if this is a mistake.'
        }
        return jsonify(resp)

    # Show last n shifts
    n = request.args.get('last_n', default=10)
    try:
        n = int(n)
    except ValueError:
        n = None
    if not isinstance(n, int) or n < 1:
        resp = {
            'status': 4,
            'message': 'Number of recent shifts must be in integer and higher than 0.'
        }
        return jsonify(resp)

    # Get recent shifts
    last_n_shifts = list_shifts(s_id, n)
    resp = {
        'status': 0,
        'name': get_name(s_id),
        'data': last_n_shifts
    }

    return jsonify(resp)


@app.route('/recognize', methods=['GET'])
def recognize_web():
    return render_template('recognize.html')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/shifts', methods=['GET'])
def shifts():
    return render_template('shifts.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
