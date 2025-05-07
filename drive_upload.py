import os
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

# Define credentials and folder IDs
CREDENTIALS_PATH = "F:/Major 2/ReviewSenseAI/credentials.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Parent Folder in Drive (Modify as needed)
MAIN_FOLDER_ID = "1YWgh_Tad2KHbxtGN4_hJdl3YvTMFsTYs"
VIDEOS_FOLDER_ID = None  # Will be set dynamically
TEXT_FOLDER_ID = None  # Will be set dynamically

# Authenticate with Google Drive
if not os.path.exists(CREDENTIALS_PATH):
    raise FileNotFoundError(f"❌ Error: Credentials file not found at {CREDENTIALS_PATH}")

creds = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)


def create_folder(folder_name, parent_id):
    """Creates a folder in Google Drive and returns the folder ID."""
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = drive_service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')


def ensure_folders_exist():
    """Ensures 'Videos' and 'Text Reviews' folders exist in Google Drive."""
    global VIDEOS_FOLDER_ID, TEXT_FOLDER_ID

    # List existing folders in main directory
    query = f"'{MAIN_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()

    existing_folders = {f["name"]: f["id"] for f in results.get("files", [])}

    # Create folders if they don't exist
    if "Videos" not in existing_folders:
        VIDEOS_FOLDER_ID = create_folder("Videos", MAIN_FOLDER_ID)
    else:
        VIDEOS_FOLDER_ID = existing_folders["Videos"]

    if "Text Reviews" not in existing_folders:
        TEXT_FOLDER_ID = create_folder("Text Reviews", MAIN_FOLDER_ID)
    else:
        TEXT_FOLDER_ID = existing_folders["Text Reviews"]


def upload_to_drive(file_path, file_name, folder_id):
    """Uploads a file to a specific Google Drive folder."""
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return None

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)

    try:
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"✅ Uploaded '{file_name}' successfully! File ID: {uploaded_file.get('id')}")
        return uploaded_file.get('id')
    except HttpError as error:
        print(f"❌ Google Drive API error: {error}")
        return None


def save_video(file_path):
    """Uploads a recorded video to the Videos folder in Drive."""
    timestamp = int(time.time())
    file_name = f"review_{timestamp}.mp4"
    return upload_to_drive(file_path, file_name, VIDEOS_FOLDER_ID)


def save_text_review(text):
    """Saves a text review as a .txt file in Google Drive."""
    timestamp = int(time.time())
    file_name = f"review_{timestamp}.txt"
    
    # Save text locally before uploading
    local_path = f"uploads/{file_name}"
    with open(local_path, "w") as text_file:
        text_file.write(text)

    return upload_to_drive(local_path, file_name, TEXT_FOLDER_ID)


# Ensure the required folders exist before uploading
ensure_folders_exist()

# Example Usage:
if __name__ == "__main__":
    # Upload a video
    video_path = "uploads/uploaded_video.mp4"
    save_video(video_path)

    # Upload a text review
    text_review = "This is a sample text review from the user."
    save_text_review(text_review)
