import argparse
import sys
import time

import cv2
from tflite_support.task import core, processor, vision

from utils import draw_detections, draw_fps
from motor import PanTilt


def build_detector(model_path: str, score_threshold: float, max_results: int):
    # this matches the style used in the TensorFlow Lite Pi example
    base_options = core.BaseOptions(
        file_name=model_path,
        num_threads=2  # keeping it small because Pi usually doesn't like huge thread counts
    )

    detection_options = processor.DetectionOptions(
        max_results=max_results,
        score_threshold=score_threshold
    )

    options = vision.ObjectDetectorOptions(
        base_options=base_options,
        detection_options=detection_options
    )

    return vision.ObjectDetector.create_from_options(options)


def parse_args():
    p = argparse.ArgumentParser(description="Project Alpha (reconstructed) - TFLite object detection")
    p.add_argument("--model", required=True, help="Path to .tflite model file")
    p.add_argument("--camera-id", type=int, default=0)
    p.add_argument("--width", type=int, default=640)
    p.add_argument("--height", type=int, default=480)
    p.add_argument("--score-threshold", type=float, default=0.30)
    p.add_argument("--max-results", type=int, default=3)
    p.add_argument("--use-gpio", action="store_true", help="Enable Raspberry Pi GPIO turret output")
    p.add_argument("--mirror", action="store_true", help="Flip camera horizontally")
    return p.parse_args()


def main():
    args = parse_args()

    cap = cv2.VideoCapture(args.camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    if not cap.isOpened():
        print("ERROR: Could not open camera. Try a different --camera-id.", file=sys.stderr)
        sys.exit(1)

    detector = build_detector(args.model, args.score_threshold, args.max_results)
    turret = PanTilt(enabled=args.use_gpio)

    # FPS counter (simple average every N frames, like in many student demos)
    fps_avg_frames = 10
    frame_count = 0
    fps = 0.0
    t0 = time.time()

    while True:
        ok, frame = cap.read()
        if not ok:
            print("ERROR: Failed to read frame from camera.", file=sys.stderr)
            break

        if args.mirror:
            frame = cv2.flip(frame, 1)

        # TFLite expects RGB, OpenCV gives BGR
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensor = vision.TensorImage.create_from_array(rgb)

        result = detector.detect(tensor)

        # Draw results on the original BGR frame for display
        draw_detections(frame, result)

        # (optional) drive turret based on where the best detection is
        turret.track(result, frame.shape)

        # FPS update
        frame_count += 1
        if frame_count % fps_avg_frames == 0:
            t1 = time.time()
            fps = fps_avg_frames / max(1e-9, (t1 - t0))
            t0 = time.time()

        draw_fps(frame, fps)

        cv2.imshow("project_alpha_detector", frame)

        # ESC to quit
        if cv2.waitKey(1) == 27:
            break

    turret.shutdown()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
