# import cv2
# import uuid

# FACE_SNAPSHOT_DIR = "face_snapshots/"


# def capture_initial_face_snapshot():
#     cap = cv2.VideoCapture(0)
#     ret, frame = cap.read()
#     if ret:
#         filename = f"{FACE_SNAPSHOT_DIR}{uuid.uuid4()}.png"
#         cv2.imwrite(filename, frame)
#         cap.release()
#         return filename
#     cap.release()
#     return None


# def detect_face():
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#     cap = cv2.VideoCapture(0)
#     ret, frame = cap.read()
#     detected = False
#     if ret:
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#         detected = len(faces) == 1
#     cap.release()
#     return detected

import cv2
import os
import json
from datetime import datetime
import threading

def capture_initial_face(face_dir, interview_id):
    cap = cv2.VideoCapture(0)
    stframe = cv2.imshow("Face Capture - Press 'c' to capture")
    captured = False

    while True:
        _, frame = cap.read()
        cv2.imshow("Face Capture - Press 'c'", frame)
        if cv2.waitKey(1) & 0xFF == ord('c'):
            path = f"{face_dir}/initial_face.jpg"
            cv2.imwrite(path, frame)
            captured = True
            break
    cap.release()
    cv2.destroyAllWindows()
    return captured

def detect_faces(frame, face_cascade):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return len(faces)

def log_face_event(face_dir, interview_id, message, frame):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    snapshot_path = f"{face_dir}/{timestamp}.jpg"
    cv2.imwrite(snapshot_path, frame)
    event_log = {
        "timestamp": timestamp,
        "snapshot": snapshot_path,
        "message": message
    }
    log_file = f"{face_dir}/face_events.json"
    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = json.load(f)
    logs.append(event_log)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=4)

def start_face_monitoring(face_dir, interview_id):
    def monitor():
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)
        while True:
            _, frame = cap.read()
            count = detect_faces(frame, cascade)
            if count == 0:
                log_face_event(face_dir, interview_id, "No face detected", frame)
            elif count > 1:
                log_face_event(face_dir, interview_id, "Multiple faces detected", frame)
            cv2.waitKey(3000)
    threading.Thread(target=monitor, daemon=True).start()
