# minimal turret output for a pan/tilt stepper setup

from dataclasses import dataclass

try:
    import RPi.GPIO as GPIO
except Exception:
    GPIO = None


@dataclass
class StepperPins:
    step: int
    direction: int
    enable: int | None = None


class Stepper:
    def __init__(self, pins: StepperPins, step_delay=0.001):
        if GPIO is None:
            raise RuntimeError("RPi.GPIO not available (are you on a Raspberry Pi?)")

        self.pins = pins
        self.step_delay = step_delay

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pins.step, GPIO.OUT)
        GPIO.setup(pins.direction, GPIO.OUT)
        if pins.enable is not None:
            GPIO.setup(pins.enable, GPIO.OUT)
            # enable is often active-low, but not always. adjust if needed
            GPIO.output(pins.enable, GPIO.LOW)

    def step(self, steps: int):
        # Positive steps = one direction, negative steps = the other.
        direction_level = GPIO.HIGH if steps > 0 else GPIO.LOW
        GPIO.output(self.pins.direction, direction_level)

        for _ in range(abs(steps)):
            GPIO.output(self.pins.step, GPIO.HIGH)
            GPIO.output(self.pins.step, GPIO.LOW)

            # Tiny delay stops the Pi from hammering the driver too fast
            # You can tune this depending on your driver/motor
            import time
            time.sleep(self.step_delay)

    def shutdown(self):
        if self.pins.enable is not None:
            GPIO.output(self.pins.enable, GPIO.HIGH)
        # GPIO.cleanup() is global, so it's better to call it once
        # from the controller rather than here


class PanTilt:
    """
    If enabled and GPIO is available, it will actually pulse step pins.
    Otherwise it prints debug output (so the script still runs on a laptop).
    """

    def __init__(self, enabled: bool = False):
        self.enabled = enabled and (GPIO is not None)

        self.pan = None
        self.tilt = None

        if self.enabled:
            # These pins are placeholder things - you must set them to match your wiring
            # Typical setup is: STEP + DIR (+ optional ENABLE) into a driver (A4988/DRV8825)
            pan_pins = StepperPins(step=17, direction=27, enable=22)
            tilt_pins = StepperPins(step=23, direction=24, enable=25)

            self.pan = Stepper(pan_pins, step_delay=0.001)
            self.tilt = Stepper(tilt_pins, step_delay=0.001)

        else:
            # "mock mode" - useful for demo/testing without hardware
            pass

    def track(self, detection_result, frame_shape):
        # Very basic tracking:
        # - choose the best detection by score
        # - nudge steppers based on where it is relative to the centre
        best = None
        best_score = -1.0

        for det in detection_result.detections:
            if not det.categories:
                continue
            score = float(det.categories[0].score or 0.0)
            if score > best_score:
                best_score = score
                best = det

        if best is None:
            return

        h, w = frame_shape[0], frame_shape[1]

        bbox = best.bounding_box
        cx = bbox.origin_x + bbox.width / 2.0
        cy = bbox.origin_y + bbox.height / 2.0

        # Normalised offset from centre (-1..1-ish)
        dx = (cx - (w / 2.0)) / (w / 2.0)
        dy = (cy - (h / 2.0)) / (h / 2.0)

        # Small proportional control (kept intentionally mild)
        k = 8  # tune this if the turret is too sluggish or too aggressive
        pan_steps = int(dx * k)
        tilt_steps = int(dy * k)

        # Deadzone stops jitter when the detection is basically centred
        deadzone = 0.10
        if abs(dx) < deadzone:
            pan_steps = 0
        if abs(dy) < deadzone:
            tilt_steps = 0

        if not self.enabled:
            # Keep this quiet (prints only when it would move)
            if pan_steps or tilt_steps:
                print(f"[mock turret] pan_steps={pan_steps:+d}, tilt_steps={tilt_steps:+d}")
            return

        # On many mounts, tilt direction feels inverted. Adjust if needed
        if pan_steps:
            self.pan.step(pan_steps)
        if tilt_steps:
            self.tilt.step(-tilt_steps)

    def shutdown(self):
        if not self.enabled:
            return

        # Clean up GPIO thing once at the end
        try:
            if self.pan:
                self.pan.shutdown()
            if self.tilt:
                self.tilt.shutdown()
        finally:
            GPIO.cleanup()
