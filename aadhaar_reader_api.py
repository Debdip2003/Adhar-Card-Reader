from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS  # Import CORS
from extract import extract_from_aadhar_images  # Your OCR function

import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/extract-aadhaar', methods=['POST'])
def extract_aadhaar():
    if 'front' not in request.files or 'back' not in request.files:
        return jsonify({"error": "Both front and back Aadhaar images are required."}), 400

    front_file = request.files['front']
    back_file = request.files['back']

    front_filename = secure_filename(front_file.filename)
    back_filename = secure_filename(back_file.filename)

    front_path = os.path.join(app.config['UPLOAD_FOLDER'], front_filename)
    back_path = os.path.join(app.config['UPLOAD_FOLDER'], back_filename)

    front_file.save(front_path)
    back_file.save(back_path)

    details = extract_from_aadhar_images(front_path, back_path)

    return jsonify(details), 200

if __name__ == '__main__':
    app.run(debug=True)
