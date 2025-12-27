import cv2

def open_camera(camera_id: int, width: int, height: int) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap
