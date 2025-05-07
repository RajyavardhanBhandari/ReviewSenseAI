from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import subprocess
import json

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'webm', 'avi', 'mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB limit (increased for video)

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function to validate file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to handle file uploads (video)
@app.route('/upload', methods=['POST'])
def upload_file():
    print("Upload endpoint called")
    print("Form data:", request.form)
    print("Files:", request.files)
    
    if 'file' not in request.files:
        print("No file part in request")
        return jsonify({'error': '❌ No file part in the request'}), 400

    file = request.files['file']
    print(f"Received file: {file.filename}")

    if file.filename == '':
        print("Empty filename")
        return jsonify({'error': '❌ No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Debugging: Check if the file is being processed
        print(f"Saving file to: {save_path}")

        try:
            file.save(save_path)
            print(f"File saved successfully to {save_path}")
            
            # Optional: Convert to MP4 if it's a WebM file
            if filename.endswith('.webm'):
                print("Converting WebM to MP4")
                mp4_path = convert_to_mp4(save_path)
                if mp4_path:
                    print(f"Conversion successful: {mp4_path}")
                    return jsonify({
                        'success': True,
                        'message': f'✅ File uploaded and converted to MP4: {mp4_path}'
                    }), 200
                else:
                    print("Conversion failed")
                    return jsonify({
                        'success': False,
                        'error': '❌ Error during conversion'
                    }), 500
            
            return jsonify({
                'success': True,
                'message': f'✅ File {filename} uploaded successfully!'
            }), 200
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return jsonify({
                'success': False,
                'error': f'❌ Error saving file: {e}'
            }), 500
    else:
        print(f"Invalid file type: {file.filename}")
        return jsonify({
            'success': False,
            'error': '❌ Invalid file type'
        }), 400

# Route to handle text reviews
@app.route('/text-review', methods=['POST'])
def text_review():
    print("Text review endpoint called")
    try:
        review_text = request.form.get('text_review', '')
        if not review_text:
            return jsonify({
                'success': False,
                'error': '❌ No text review provided'
            }), 400
            
        # Save the text review to a file
        review_filename = f"review_{int(time.time())}.txt"
        review_path = os.path.join(app.config['UPLOAD_FOLDER'], review_filename)
        
        with open(review_path, 'w') as f:
            f.write(review_text)
            
        return jsonify({
            'success': True,
            'message': '✅ Text review saved successfully!'
        }), 200
    except Exception as e:
        print(f"❌ Error saving text review: {e}")
        return jsonify({
            'success': False,
            'error': f'❌ Error saving text review: {e}'
        }), 500

def convert_to_mp4(webm_path):
    mp4_path = webm_path.replace('.webm', '.mp4')

    # Call ffmpeg to convert
    try:
        result = subprocess.run(
            ['ffmpeg', '-i', webm_path, mp4_path], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        print(result.stdout.decode())  # Log stdout from ffmpeg
        print(result.stderr.decode())  # Log stderr from ffmpeg
        return mp4_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Conversion failed: {e.stderr.decode()}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    import time  # Add this import at the top
    app.run(debug=True)