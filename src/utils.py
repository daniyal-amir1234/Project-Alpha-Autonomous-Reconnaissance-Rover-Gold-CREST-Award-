import cv2


FONT = cv2.FONT_HERSHEY_SIMPLEX

def draw_fps(frame, fps: float):
    text = f"FPS: {fps:.1f}"
    cv2.putText(frame, text, (10, 25), FONT, 0.7, (0, 0, 255), 2)


def draw_detections(frame, detection_result):
    """
    Draw bounding boxes + labels.
    detection_result is a tflite_support.task.vision.DetectionResult.
    """
    for det in detection_result.detections:
        bbox = det.bounding_box
        x1, y1 = bbox.origin_x, bbox.origin_y
        x2, y2 = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # category list is usually non-empty, but let's not assume that
        if det.categories:
            cat = det.categories[0]
            name = cat.category_name or "object"
            score = float(cat.score) if cat.score is not None else 0.0

            label = f"{name} {score:.2f}"
            # put label slightly above box, but don't go off-screen
            label_y = y1 - 8 if y1 - 8 > 10 else y1 + 20
            cv2.putText(frame, label, (x1, label_y), FONT, 0.6, (0, 0, 255), 2)
