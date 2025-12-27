# Project Alpha — Autonomous Reconnaissance Rover
Sep 2023 – Jul 2024

## Overview
Awarded: Gold CREST Award (Engineering Education Scheme)

Project Alpha is an autonomous reconnaissance rover developed as part of the Engineering Education Scheme (EES) and awarded the Gold CREST Award. The system combines a manually driven rover platform with an AI-powered sentry turret, capable of real-time object detection and tracking using TensorFlow Lite and OpenCV running on a Raspberry Pi. The turret uses stepper motors for pan/tilt actuation and a USB webcam for live vision input.

In a multidisciplinary team of 7 engineers, computer scientists and physicists, we built a reconnaissance rover with a camera 'sentry' turret: the rover platform was manually controlled, while the turret performed real-time object detection and basic target tracking using TensorFlow Lite + OpenCV on a Raspberry Pi.

## Features
- Real-time object detection (TensorFlow Lite Task Library)
- Webcam / Pi camera capture (OpenCV)
- FPS counter overlay (matches recovered screenshot structure)
- Optional pan/tilt tracking interface (GPIO stepper control stubbed + mock driver)

## Tech
- Python
- OpenCV
- TensorFlow Lite / tflite-support (Task library)
- Raspberry Pi GPIO

## Quick start (Laptop / Desktop)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m src.main --model assets/models/efficientdet_lite0.tflite
