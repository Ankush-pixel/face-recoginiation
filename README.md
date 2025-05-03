Deep Learning Face Recognition System
This project is a web-based Deep Learning Face Recognition System built using Flask for the backend and HTML/CSS/JavaScript for the frontend. It integrates five advanced deep learning models for real-time face detection, face recognition, and facial attribute analysis.

Features
 Face Detection using RetinaFace
 
Face Recognition using:
ArcFace
FaceNet
OpenFace

Liveness Detection (anti-spoofing) to identify fake or replayed faces
 Mask Detection to identify partially covered faces
 Age, Gender, and Emotion Analysis (optional if models support)
 Upload or capture photo via webcam (PWA-friendly)
 Result summary with predictions and visualizations

 Fallback error page for invalid inputs or detection failure

 Models Used
ArcFace – Cutting-edge face recognition model known for high accuracy
FaceNet – Embedding-based verification using triplet loss
OpenFace – Lightweight and efficient face embedding model
Liveness Detection Model – Detects spoof or presentation attacks
Mask Detection Model – Identifies whether the face is masked or unmasked

Project Structure
├── app.py                  # Flask backend server
├── static/                 # CSS, JavaScript, and media assets
├── templates/
│   ├── index.html          # Main interface for image upload or camera capture
│   ├── result.html         # Results with face analysis and matching
│   └── error.html          # Shown when detection/processing fails
├── models/                 # Folder for all pre-trained model files
├── uploads/                # Temporary storage for user-uploaded images
├── requirements.txt        # List of required Python packages
└── README.md               # Project documentation (this file)

Installation

1. **Clone the Repository:**

```bash
git clone https://github.com/ankush-pixel/face-recognition-system.git
cd face-recognition-system
install Dependencies:```

**bash**
pip install -r requirements.txt

4. Download Pre-trained Models:
Place all required pre-trained models in the models/ directory. You may need to manually download ArcFace, FaceNet, OpenFace, and other model weights as per licensing.
5.Run the Application:
python app.py
