from flask import Flask, request, render_template, jsonify
from flask_cors import CORS  # Enable CORS for frontend
import os
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for JavaScript frontend

# Set up paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
TEXT_REVIEWS_FILE = os.path.join(UPLOAD_FOLDER, "text_reviews.txt")

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Google Drive API Configuration
CREDENTIALS_PATH = "F:/Major 2/ReviewSenseAI/credentials.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID = "1YWgh_Tad2KHbxtGN4_hJdl3YvTMFsTYs"

# Verify credentials file exists
if not os.path.exists(CREDENTIALS_PATH):
    raise FileNotFoundError(f"❌ Error: Credentials file not found at {CREDENTIALS_PATH}")

creds = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

def upload_to_drive(file_path, file_name, folder_id=FOLDER_ID):
    """Uploads a file to Google Drive with a retry mechanism."""
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return None

    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)

    for attempt in range(3):  # Retry up to 3 times
        try:
            uploaded_file = drive_service.files().create(
                body=file_metadata, media_body=media, fields='id'
            ).execute()
            print(f"✅ File uploaded successfully! File ID: {uploaded_file.get('id')}")
            return uploaded_file.get('id')
        except HttpError as error:
            print(f"⚠️ Upload failed, attempt {attempt + 1}: {error}")
            time.sleep(2)  # Wait before retrying
    return None  # Return None after 3 failed attempts

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    return '', 204  # Prevent 404 error for favicon

@app.route("/upload", methods=["POST"])
def upload_video():
    print("📌 Received a request to /upload")  # Debugging print

    if "file" not in request.files or request.files["file"].filename == "":
        return jsonify({"error": "No file selected"}), 400

    file = request.files["file"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"video_{timestamp}.mp4"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)

    print(f"📂 Saving file to: {file_path}")

    try:
        file.save(file_path)
        print("✅ File saved successfully!")

        # Upload to Google Drive
        drive_file_id = upload_to_drive(file_path, file_name)

        if drive_file_id:
            return jsonify({"message": "Video uploaded successfully!", "drive_file_id": drive_file_id}), 200
        else:
            return jsonify({"error": "Failed to upload to Google Drive"}), 500
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return jsonify({"error": f"File save error: {e}"}), 500

@app.route("/submit_review", methods=["POST"])
def submit_review():
    review = request.form.get("text_review", "").strip()

    if not review:
        return jsonify({"error": "Empty review cannot be submitted"}), 400

    try:
        with open(TEXT_REVIEWS_FILE, "a", encoding="utf-8") as f:
            f.write(review + "\n")
        print("✅ Review saved successfully!")
    except Exception as e:
        print(f"❌ Error saving review: {e}")
        return jsonify({"error": "Error saving review"}), 500

    drive_file_id = upload_to_drive(TEXT_REVIEWS_FILE, "text_reviews.txt")

    if drive_file_id:
        return jsonify({"message": "Review submitted successfully!", "drive_file_id": drive_file_id}), 200
    else:
        return jsonify({"error": "Failed to upload review to Google Drive"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Ensure Flask runs on port 5000
