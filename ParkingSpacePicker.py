import cv2
import pickle
import numpy as np

# Load or initialize the list for parking spaces
try:
    with open("CarParkPos", "rb") as f:
        posList = pickle.load(f)
except:
    posList = []

current_zone = []  # Temporarily store points for the current parking space

# Button position and size for toggling modes
button_parking = (20, 20, 150, 60)  # x, y, width, height


def mouseClick(event, x, y, flags, params):
    global current_zone

    if event == cv2.EVENT_LBUTTONDOWN:
        # Check if the click is on the parking mode button
        if (
            button_parking[0] <= x <= button_parking[0] + button_parking[2]
            and button_parking[1] <= y <= button_parking[1] + button_parking[3]
        ):
            print("Parking space selection mode.")
            return

        # Add point to the current zone
        current_zone.append((x, y))

        # Once four points are selected, add them as a parking space
        if len(current_zone) == 4:
            posList.append(current_zone)
            print(f"New parking space added: {current_zone}")
            current_zone = []  # Reset for the next parking space

    elif event == cv2.EVENT_RBUTTONDOWN:
        # Right-click to remove a parking space
        removed = False  # Flag to check if a space was removed
        for i, space in enumerate(posList):
            # Check if the click is near any of the four points
            if any(
                np.linalg.norm(np.array([px, py]) - np.array([x, y])) < 15
                for px, py in space
            ):
                print(f"Removing parking space: {space}")
                posList.pop(i)
                removed = True
                break

        if not removed:
            print("No parking space found near the clicked point.")

    # Save parking positions
    with open("CarParkPos", "wb") as f:
        pickle.dump(posList, f)


def draw_x_marker(img, point, size=5):
    """Draws an 'X' marker at a given point."""
    x, y = point
    cv2.line(img, (x - size, y - size), (x + size, y + size), (0, 0, 255), 2)
    cv2.line(img, (x + size, y - size), (x - size, y + size), (0, 0, 255), 2)


def draw_buttons(img):
    """Draws the mode toggle button."""
    # Draw the parking button
    cv2.rectangle(
        img,
        (button_parking[0], button_parking[1]),
        (button_parking[0] + button_parking[2], button_parking[1] + button_parking[3]),
        (0, 255, 0),
        -1,
    )
    cv2.putText(
        img,
        "Parking Mode",
        (button_parking[0] + 10, button_parking[1] + 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 0),
        2,
    )


while True:
    img = cv2.imread("carParkImg.png")

    # Draw all saved parking spaces
    for space in posList:
        if len(space) == 4:
            pts = np.array(space, np.int32)
            cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            for point in space:
                draw_x_marker(img, point)

    # Draw points for the current space being selected
    for point in current_zone:
        cv2.circle(
            img, point, 5, (255, 0, 0), cv2.FILLED
        )  # Blue circles for selected points

    # Draw the toggle button
    draw_buttons(img)

    # Show the current image
    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)
    key = cv2.waitKey(1)

    if key == 27:  # Press Esc to exit
        break
