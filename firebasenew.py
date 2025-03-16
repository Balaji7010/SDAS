import cv2
import numpy as np
import dlib
from imutils import face_utils
import firebase_admin
from firebase_admin import credentials, firestore, db
import time
import os
import threading
import serial
import re
import logging
from playsound import playsound  # Ensure this is installed: pip install playsound

# Initialize Logging
logging.basicConfig(filename="drowsiness.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Initialize Firebase
cred = credentials.Certificate("/home/rpi/sdas-c728e-firebase-adminsdk-fbsvc-767bc08163.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://sdas-c728e-default-rtdb.firebaseio.com/"
})
ref = db.reference("/driver_status")
db = firestore.client()

# GPS Configuration
GPS_PORT = "ttyS0"  # ✅ Replace with correct GPS module port
GPS_BAUDRATE = 9600
gps_data = {"lat": None, "lon": None}

# Load Face Landmark Model
MODEL_PATH = r"C:\Users\DHANUSH\OneDrive\Desktop\dhanush\Driver-Drowsiness-Detection\shape_predictor_68_face_landmarks.dat"
ALERT_THRESHOLD_SECONDS = 15

# Function to Extract GPS Data
def parse_gps_data(nmea_sentence):
    match = re.search(r'\$G[N|P]GGA,\d+\.\d+,(\d{2})(\d{2}\.\d+),([NS]),(\d{3})(\d{2}\.\d+),([EW])', nmea_sentence)
    if match:
        lat_deg, lat_min, lat_dir, lon_deg, lon_min, lon_dir = match.groups()
        lat = float(lat_deg) + float(lat_min) / 60
        lon = float(lon_deg) + float(lon_min) / 60
        if lat_dir == 'S':
            lat = -lat
        if lon_dir == 'W':
            lon = -lon
        return lat, lon
    return None, None

# GPS Thread to Continuously Update Data
def update_gps():
    global gps_data
    try:
        gps_serial = serial.Serial(GPS_PORT, GPS_BAUDRATE, timeout=3)
        while True:
            try:
                line = gps_serial.readline().decode("utf-8", errors="ignore").strip()
                if "$GNGGA" in line or "$GPGGA" in line:
                    lat, lon = parse_gps_data(line)
                    if lat and lon:
                        gps_data["lat"], gps_data["lon"] = lat, lon
                        logging.info(f"📍 GPS Updated: Lat={lat}, Lon={lon}")
                    else:
                        logging.warning("⚠️ GPS Data Invalid. Retaining last known coordinates.")
            except Exception as e:
                logging.error(f"GPS Read Error: {e}")
            time.sleep(1)
    except Exception as e:
        logging.error(f"GPS Initialization Error: {e}")

gps_thread = threading.Thread(target=update_gps, daemon=True)
gps_thread.start()

# Send Data to Firebase (Optimized to send only when status changes)
prev_status = None

def send_data_to_firebase(status, lat, lon):
    global prev_status
    if status != prev_status:
        doc_ref = db.collection("driver_status").document("current_status")
        doc_ref.set({
            "driverStatus": status,
            "latitude": lat,
            "longitude": lon,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        logging.info(f"✅ Data sent to Firebase: {status}, Lat={lat}, Lon={lon}")
        prev_status = status

# Eye Aspect Ratio Calculation
def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)

# Drowsiness Detection
def detect_drowsiness():
    print("🚀 Starting Drowsiness Detection...")
    drowsy_time = 0
    sleep_time = 0

    detector = dlib.get_frontal_face_detector()
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Error: Shape predictor file not found at {MODEL_PATH}")
        return
    predictor = dlib.shape_predictor(MODEL_PATH)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Cannot access webcam")
        return

    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Frame capture failed")
            break
        
        frame = cv2.resize(frame, (480, 360))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        # Default GPS values
        lat, lon = gps_data["lat"], gps_data["lon"]

        status_data = {
            "driverStatus": "Active",
            "eyeStatus": "Open",
            "drowsinessLevel": "Low",
            "drowsinessAlert": "No Alert",
        }

        if faces:
            for face in faces:
                landmarks = face_utils.shape_to_np(predictor(gray, face))
                left_eye = landmarks[lStart:lEnd]
                right_eye = landmarks[rStart:rEnd]
                EAR = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0

                if EAR < 0.23:
                    drowsy_time += 1
                    sleep_time = 0
                    if drowsy_time >= 5:
                        status_data.update({
                            "driverStatus": "Drowsy",
                            "eyeStatus": "Closed",
                            "drowsinessAlert": "Drowsy Alert",
                            "drowsinessLevel": "High",
                        })
                        playsound(r"C:\Users\DHANUSH\OneDrive\Desktop\final_year_project\Driver-Drowsiness-Detection\alarm.mp3")
  # Add an alert sound

                elif EAR < 0.15:
                    sleep_time += 1
                    drowsy_time = 0
                    if sleep_time >= 8:
                        status_data.update({
                            "driverStatus": "Sleeping",
                            "eyeStatus": "Closed",
                            "drowsinessAlert": "Sleeping Alert",
                            "drowsinessLevel": "Critical",
                        })
                        playsound(r"C:\Users\DHANUSH\OneDrive\Desktop\final_year_project\Driver-Drowsiness-Detection\alarm.mp3")
  # Add an alert sound

                else:
                    drowsy_time = sleep_time = 0
                    status_data.update({
                        "driverStatus": "Active",
                        "eyeStatus": "Open",
                        "drowsinessAlert": "No Alert",
                        "drowsinessLevel": "Low",
                    })

                cv2.putText(frame, f"Status: {status_data['driverStatus']}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Send Data to Firebase (Only if status changes)
        send_data_to_firebase(status_data["driverStatus"], lat, lon)

        cv2.imshow("Driver Monitoring", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🛑 Drowsiness detection stopped.")

if _name_ == "_main_":
    detect_drowsiness()