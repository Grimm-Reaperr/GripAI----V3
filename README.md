# GripAI----V3
Version 3 Without Reference Object Hand Measurement 

# Hand Measurement Tool using MediaPipe

This project captures hand measurements (width and height in inches) using a webcam and MediaPipe. It auto-saves an image when the hand is correctly positioned in a virtual reference box.

## Features
- Real-time hand detection and tracking
- Converts pixel distance to centimeters/inches using a calibrated box
- Automatically saves hand image if placement is correct


Real-Time User Guidance for Hand Measurement:

1) Ensure your laptop or webcam is stable. A fixed camera ensures consistent
scaling and accurate measurements.
2) Avoid excessive brightness, glare, or shadows. Use soft, even lighting for
accurate hand detection.
3) Keep your palm and fingers directly facing the camera. Avoid tilting, as angles
can affect measurement accuracy.
4)For accurate scaling, place your hand close enough to the camera so that it
nearly fills the box without crossing the edges.
5)Stay still during the countdown. Movement can cause inaccurate readings or
cancel the capture.
6)To ensure accurate hand measurement, use a clean background, like a plain
wall or desk, to avoid detection confusion.


## How to Run

1. Clone the repository:
```bash
git clone https://github.com/your-username/hand-measurement.git
cd hand-measurement 
