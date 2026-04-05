from flask import Flask, render_template, Response, request
import cv2
from ultralytics import YOLO
import numpy as np
import time

app = Flask(__name__)

# MODEL & CAMERA CONFIGURATION

model = YOLO("yolo11s.pt")  #user must download manually
camera_source = 0  # Laptop webcam
last_slots = []
last_counts = (0, 0, 4)  # free, occupied, total
last_detection_time = time.time()
stability_buffer = []  # for detection smoothing

def get_camera(src):
    cap = cv2.VideoCapture(src)
    return cap if cap.isOpened() else None

# DETECTION & SLOT TRACKING
def detect(frame):
    global last_slots, last_counts, last_detection_time, stability_buffer

    # Run YOLOv11 detection
    results = model(frame, imgsz=720, verbose=False)[0]
    detections = []

    for box in results.boxes:
        cls = int(box.cls)
        label = model.names[cls]
        if label in ("car", "motorcycle", "bus", "truck", "bicycle"):
            detections.append(box.xyxy[0].cpu().numpy())

    h, w, _ = frame.shape
    ry1, ry2 = int(h * 0.60), int(h * 0.92)

    centers = []
    for (x1, y1, x2, y2) in detections:
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        if ry1 <= cy <= ry2:
            centers.append(cx)
            cv2.circle(frame, (cx, cy), 6, (0, 255, 0), -1)

    centers.sort()

    # Determine slot configuration
    if len(centers) > 0:
        diffs = np.diff(centers)
        avg_gap = int(np.mean(diffs)) if len(diffs) > 0 else 180
        avg_gap = max(120, min(avg_gap, 280))
        slot_count = max(4, min(10, w // avg_gap))
    else:
        slot_count = last_counts[2]

    slot_width = w // slot_count
    occupied = []

    for i in range(slot_count):
        sx1, sx2 = i * slot_width, (i + 1) * slot_width
        occ = any(sx1 <= cx <= sx2 for cx in centers)
        occupied.append(occ)
        color = (0, 0, 255) if occ else (0, 255, 0)
        cv2.rectangle(frame, (sx1, ry1), (sx2, ry2), color, 2)
        cv2.putText(frame, f"S-{i+1}", (sx1 + 10, ry1 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    free = occupied.count(False)
    used = occupied.count(True)

    # === Stabilization: Smooth results over time === #
    stability_buffer.append((free, used, slot_count))
    if len(stability_buffer) > 10:
        stability_buffer.pop(0)

    avg_free = int(np.mean([v[0] for v in stability_buffer]))
    avg_used = int(np.mean([v[1] for v in stability_buffer]))
    avg_total = int(np.mean([v[2] for v in stability_buffer]))
    # Update global counts
    last_counts = (avg_free, avg_used, avg_total)
    last_detection_time = time.time()
    # === Dashboard Overlay === #
    cv2.putText(frame, f"FREE: {avg_free}", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    cv2.putText(frame, f"OCCUPIED: {avg_used}", (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    cv2.putText(frame, f"TOTAL: {avg_total}", (30, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

    if avg_free > 0:
        next_slot = occupied.index(False) + 1
        cv2.putText(frame, f"→ PARK IN SLOT S-{next_slot}", (30, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
    else:
        cv2.putText(frame, "LOT FULL", (30, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    return frame
# VIDEO STREAM
def frame_stream():
    cap = get_camera(camera_source)
    while True:
        if cap is None or not cap.isOpened():
            cap = get_camera(camera_source)
            continue

        success, frame = cap.read()
        if not success:
            continue

        frame = detect(frame)
        ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame = buffer.tobytes()

        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
# ROUTES
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/status")
def status():
    return {
        "free": last_counts[0],
        "occupied": last_counts[1],
        "total": last_counts[2],
        "last_update": round(time.time() - last_detection_time, 2)
    }
@app.route("/video_feed")
def video_feed():
    return Response(frame_stream(), mimetype="multipart/x-mixed-replace; boundary=frame")
if __name__ == "__main__":
    print("Smart Parking System AI starting...")
    print("🌐 Visit http://127.0.0.1:5000 or your local IP address")
    app.run(host="0.0.0.0", port=5000)
