# test_yolo.py
import os
from ultralytics import YOLO
import cv2
import numpy as np

# ----------------------------
# CONFIG
# ----------------------------
MODEL_PATH = "models/clash_digits_11.pt"        # path to your trained YOLO model
TEST_IMAGES_DIR = "clash_digit_detection/test/images"  # folder with test images
OUTPUT_DIR = "runs/detect/test_results"      # folder to save annotated images
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------
# LOAD MODEL
# ----------------------------
model = YOLO(MODEL_PATH)
print(f"Loaded model: {MODEL_PATH}")

# ----------------------------
# RUN PREDICTIONS
# ----------------------------
for filename in os.listdir(TEST_IMAGES_DIR):
    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
        continue

    img_path = os.path.join(TEST_IMAGES_DIR, filename)
    print(f"\nProcessing: {img_path}")

    results = model.predict(img_path)  # returns list of Results objects
    result = results[0]                 # get first (and usually only) result

    # Print detected digits
    if len(result.boxes) == 0:
        print("No digits detected!")
    else:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            cls_name = result.names[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            print(f"Digit: {cls_name}, Conf: {conf:.2f}, Box: [{x1},{y1},{x2},{y2}]")

    # Annotate image
    annotated_img = result.plot()  # BGR numpy array

    # Save annotated image
    save_path = os.path.join(OUTPUT_DIR, filename)
    cv2.imwrite(save_path, annotated_img)
    print(f"Saved annotated image: {save_path}")
