import cv2
import numpy as np
from keras.models import model_from_json

# Load the CNN model
with open('model.json', 'r') as json_file:
    model_json = json_file.read()
model = model_from_json(model_json)
model.load_weights('model.weights.h5')

# Load the Haar Cascade classifier
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Define emotion labels
emotions = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}

# Open the video capture
cap = cv2.VideoCapture(0)  # Use 0 for webcam, or provide a video file path

while True:
    # Read a frame from the video capture
    ret, frame = cap.read()

    if not ret:
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Process each detected face
    for (x, y, w, h) in faces:
        # Extract the face region from the frame
        face_region = gray[y:y+h, x:x+w]

        # Preprocess the face image and predict the emotion
        face_image = cv2.resize(face_region, (48, 48))
        face_image = face_image.reshape((1, 48, 48, 1)) / 255.0
        predictions = model.predict(face_image)

        # Get the predicted emotion label and confidence score
        predicted_emotion = emotions[np.argmax(predictions)]
        confidence_score = max(predictions[0]) * 100

        # Draw a bounding box and add the emotion label and confidence score
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, f"{predicted_emotion} ({confidence_score:.2f}%)", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

    # Display the processed frame
    cv2.imshow('Emotion Detection', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close the window
cap.release()
cv2.destroyAllWindows()