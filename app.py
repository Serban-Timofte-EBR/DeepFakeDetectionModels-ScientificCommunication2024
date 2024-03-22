from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
sys.path.insert(0, '../')

from GPTmodel import predict_image
from GPTmodel import load_trained_model, predict_image


model = load_trained_model('../deepfake_detector_model.h5')
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'No selected file or file type not allowed'}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    prediction = predict_image(model, file_path)
    
    os.remove(file_path)
    
    if prediction < 0.5:
        result = 'Deepfake Detected'
        confidence = 1 - prediction 
    else:
        result = 'Real Photo'
        confidence = prediction

    return jsonify({'result': result, 'confidence': float(confidence)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)