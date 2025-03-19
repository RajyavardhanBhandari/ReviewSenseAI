from flask import Flask, request
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'service.json'  # Path to your service account file

def authenticate_gdrive():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return 'No video file uploaded.', 400

    video_file = request.files['video']
    video_file.save('uploaded_video.webm')  # Save temporarily

    # Specify your folder ID here
    PARENT_FOLDER_ID = "your_folder_id_here"

    # Upload to Google Drive
    drive_service = authenticate_gdrive()
    file_metadata = {
        'name': 'uploaded_video.webm',
        'parents': [PARENT_FOLDER_ID]  # Specify the parent folder
    }
    media = MediaFileUpload('uploaded_video.webm', mimetype='video/webm')
    drive_service.files().create(body=file_metadata, media_body=media).execute()

    os.remove('uploaded_video.webm')  # Clean up
    return 'Video uploaded successfully!', 200

if __name__ == '__main__':
    app.run(debug=True)