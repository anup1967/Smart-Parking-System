Smart Parking System:
AI-powered smart parking system using YOLO and OpenCV to detect vehicles and monitor parking slot occupancy in real time. The system processes live camera input and displays available and occupied slots through a Flask-based web interface.

Development Environment:
This project was developed and tested using Visual Studio Code.
You can run it in any Python-supported IDE, but VS Code is recommended for consistency.

Requirements:
Make sure the following are available on your system:

Python (recommended 3.8 or above)
All dependencies listed in requirements.txt

The project uses:
1.Flask for backend and streaming
2.OpenCV for video processing
3.Ultralytics YOLO for object detection
4.NumPy for calculations
5.Missing Files and Folders

IMPORTANT
Some files are intentionally not included in this repository:
1.yoloenv/
Virtual environment folder. It is system-specific and should be created locally.
2.runs/
Automatically generated during model execution. Stores detection outputs.
3.yolo11s.pt
YOLO model file. This file is large and must be downloaded separately.

After downloading the model file, place it in the root directory:

Smart-Parking-System/yolo11s.pt
Project Structure
Smart-Parking-System/
│
├── app.py                # Main Flask application
├── requirements.txt     # Dependencies
├── config.json          # Camera configuration
├── coco_labels.json     # Class labels for detection
│
├── templates/           # HTML templates
│   └── index.html
│
├── static/              # Static assets (CSS, JS, etc.)
│   └── (optional files)
│
├── .gitignore
└── README.md

How the System Works:
The YOLO model detects vehicles such as cars, motorcycles, buses, and trucks
The frame is divided into multiple parking slots dynamically
Vehicle positions are mapped to these slots

Each slot is classified as:
Free
Occupied

A smoothing mechanism is applied to stabilize detection results
The results are displayed on a live video feed

How to Run:
1. Create a virtual environment
python -m venv yoloenv

3. Activate the environment

Windows:
yoloenv\Scripts\activate

Mac/Linux:
source yoloenv/bin/activate

3. Install dependencies:
pip install -r requirements.txt

4. Add the model file:
Place yolo11s.pt in the root directory (same location as app.py).

5. Run the application:
python app.py

7. Open in browser:
http://127.0.0.1:5000

API Endpoint
/status
Returns the current parking status in JSON format:
{
  "free": number,
  "occupied": number,
  "total": number,
  "last_update": seconds
}

Notes:
1.Ensure the camera is accessible before running the application
2.The default camera source is set to the system webcam
3.You can modify camera inputs inside config.json
4.Performance depends on system hardware and camera quality
