# 🖐️ Gesture Drawing App 🎨

A Python-based gesture-controlled drawing app using your webcam and hand gestures. 
Built with **MediaPipe**, **OpenCV**, and **Pygame**.
This project lets you draw, paint, and switch tools using simple hand signs.

---

## 🚀 Features

- 👆 Draw using your index finger
- 🔁 Change brush color with thumb rotation
- ✌️ Draw shapes with finger combinations:
  - Circle Tool: Index + Middle fingers
  - Rectangle Tool: Index + Pinky fingers
- ✨ Switch brush styles with hand signs:
  - Peace ✌️ = Dashed Brush
  - Rock 🤘 = Spray Paint Brush
- 👁️ Real-time webcam feed + Drawing canvas
- 💾 Save your canvas as PNG with `S` key
- 🧼 Clear canvas with `C` key
- 🔚 Exit with `Q` key

---

## 📦 Requirements

Make sure you have **Python 3.7+** installed.

Install dependencies:
```bash
pip install opencv-python mediapipe pygame

##

git clone https://github.com/spade-codee/gesture-drawing-app.git
cd gesture-drawing-app

