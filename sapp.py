import streamlit as st
import os
import cv2
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Function to authenticate Google Drive API
def authenticate_gdrive():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    creds = flow.run_local_server(port=0)
    return build('drive', 'v3', credentials=creds)

# Function to upload file to Google Drive
def upload_to_drive(file_name):
    #pip install google-api-python-client
    from googleapiclient.discovery import build
    from google.oauth2 import service_account

    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'service.json'
    PARENT_FOLDER_ID = "1aFtYe25gXUucJgBJw_GrNRUDEAdoMhpB"

    def authenticate():
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return creds

    def upload_photo(file_path):
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name' : "Review.mp4",
            'parents' : [PARENT_FOLDER_ID]
        }

        file = service.files().create(
            body=file_metadata,
            media_body=file_path
        ).execute()

    upload_photo("recorded_video.mp4")


# Streamlit UI
st.title("Webcam Video Recorder")

if st.button("Start Recording", key='start'):
    st.session_state.recording = True
    st.session_state.video_file = 'recorded_video.mp4'  # Set video file name
    st.write("Recording... Press 'Stop Recording' to end.")

    # Start video capture
    v = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(st.session_state.video_file, fourcc, 30, (640, 480))

    while st.session_state.get('recording', False):
        ret, frame = v.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        out.write(frame)
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    v.release()
    out.release()
    cv2.destroyAllWindows()
    st.write("Recording stopped.")

if st.button("Stop Recording", key='stop'):
    st.session_state.recording = False

if st.button("Upload to Drive", key='upload'):
    if os.path.exists(st.session_state.video_file):
        video_id = upload_to_drive(st.session_state.video_file)
        st.success(f"Video uploaded successfully! File ID: {video_id}")
    else:
        st.error("No video file found to upload.")

# import streamlit as st
# import os
# import cv2
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload

# # Function to authenticate Google Drive API
# def authenticate_gdrive():
#     SCOPES = ['https://www.googleapis.com/auth/drive.file']
#     SERVICE_ACCOUNT_FILE = 'service.json'
#     creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#     return build('drive', 'v3', credentials=creds)

# # Function to upload file to Google Drive
# def upload_to_drive(file_name):
#     drive_service = authenticate_gdrive()
#     file_metadata = {
#         'name': os.path.basename(file_name),
#         'parents': "1aFtYe25gXUucJgBJw_GrNRUDEAdoMhpB" # Replace with your folder ID
#     }
#     media = MediaFileUpload(file_name, mimetype='video/mp4')
#     file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     return file.get('id')

# # Streamlit UI
# st.title("Webcam Video Recorder")

# # Create a sidebar for controls
# start_button = st.sidebar.button("Start Recording", key='start')
# stop_button = st.sidebar.button("Stop Recording", key='stop')
# upload_button = st.sidebar.button("Upload to Drive", key='upload')

# if 'recording' not in st.session_state:
#     st.session_state.recording = False

# # Start recording
# if start_button and not st.session_state.recording:
#     st.session_state.recording = True
#     st.session_state.video_file = 'recorded_video.mp4'  # Set video file name
#     st.write("Recording...")

#     # Start video capture
#     v = cv2.VideoCapture(0)
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Change codec for mp4
#     out = cv2.VideoWriter(st.session_state.video_file, fourcc, 30, (640, 480))

#     while st.session_state.recording:
#         ret, frame = v.read()
#         if not ret:
#             break

#         frame = cv2.flip(frame, 1)
#         out.write(frame)

#         # Convert frame to RGB and display in Streamlit
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         st.image(frame_rgb, channels="RGB")

#         # Check for stop condition
#         if stop_button:
#             st.session_state.recording = False
#             break

#     v.release()
#     out.release()
#     st.write("Recording stopped.")

# # Stop recording
# if stop_button and st.session_state.recording:
#     st.session_state.recording = False

# # Upload to Google Drive
# if upload_button:
#     if os.path.exists(st.session_state.video_file):
#         video_id = upload_to_drive(st.session_state.video_file)
#         st.success(f"Video uploaded successfully! File ID: {video_id}")
#     else:
#         st.error("No video file found to upload.")