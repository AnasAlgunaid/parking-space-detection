import cv2
import pickle
import numpy as np
from ultralytics import YOLO
import requests

API_URL = "http://127.0.0.1:8000/update"


def send_parking_data(free_spaces, total_spaces):
    """Send parking data to the backend."""
    data = {
        "spaces": [
            {"id": i, "status": "free" if i < free_spaces else "occupied"}
            for i in range(total_spaces)
        ],
        "total": total_spaces,
        "free": free_spaces,
        "occupied": total_spaces - free_spaces,
    }
    print("Sending data:", data)  # Debugging log
    try:
        response = requests.post(API_URL, json=data)
        print("Response:", response.status_code, response.text)  # Debugging log
    except Exception as e:
        print("Failed to send data:", e)


# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Load parking spaces and restricted zones
with open("CarParkPos", "rb") as f:
    posList = pickle.load(f)

cap = cv2.VideoCapture("carPark.mp4")


def detect_cars(img):
    results = model(img, stream=True)
    vehicles = []  # Collect all detected vehicles
    for result in results:
        for box in result.boxes:
            # Check if the detected object is a car, motorcycle, bus, or truck
            if int(box.cls) in [2, 3, 5, 7]:
                vehicles.append(box.xyxy.numpy()[0])  # Extract bounding box
    return vehicles


def checkParkingSpace(img, car_boxes):
    spaceCounter = 0  # Count of free spaces

    for space in posList:
        pts = np.array(space, np.int32)
        rect = cv2.boundingRect(pts)

        x, y, width, height = rect
        parking_polygon = np.array(space, np.int32)

        # Check if the parking space is occupied
        occupied = any(
            cv2.pointPolygonTest(
                parking_polygon, ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), False
            )
            >= 0
            for box in car_boxes
        )

        # Set the color based on the occupancy status
        color = (0, 0, 255) if occupied else (0, 255, 0)
        if not occupied:
            spaceCounter += 1  # Increment free space counter

        # Draw the parking space polygon
        cv2.polylines(img, [pts], isClosed=True, color=color, thickness=2)

    # Display the number of free spaces on the video
    cv2.putText(
        img,
        f"Free Spaces: {spaceCounter}/{len(posList)}",
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2,
    )

    return spaceCounter  # Return the count of free spaces


while True:
    success, img = cap.read()
    if not success:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # Detect cars
    car_boxes = detect_cars(img)

    # Check parking spaces and get the number of free spaces
    free_spaces = checkParkingSpace(img, car_boxes)

    # Send parking data to the backend
    send_parking_data(free_spaces, len(posList))

    # Display the video feed with parking status
    cv2.imshow("Parking Lot", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
