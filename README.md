Real-Time Biometric Face Recognition & Verification System

This is a comprehensive, full-stack web application designed for high-accuracy human face recognition and verification. It uses a Python/Flask backend for scalable real-time processing and a modern JavaScript frontend for live webcam integration via WebRTC and WebSockets.

The system is engineered with robust security, featuring Liveness Detection to prevent spoofing and secure storage of facial embeddings.

🚀 Key Features

Real-Time Biometric Verification (1:1): Confirming identity against a claimed user profile.

Real-Time Identification (1:N): Identifying a user from the entire database instantly.

High-Accuracy CV Pipeline: Utilizes deep learning models for generating unique 128-dimensional facial embeddings.

Spoofing Prevention: Includes a basic Liveness Detection mechanism during the verification phase.

Secure Authentication: User registration, password hashing, and encrypted storage of biometric data.

Low-Latency Stream: Communication handled via WebSockets for smooth real-time performance.

🏛️ Architecture Overview

The application follows a modular, client-server architecture:

Component

Role

Technologies

Frontend (Client)

Captures video stream, handles user interaction, and displays real-time feedback.

HTML5, CSS3 (Tailwind CSS for styling), JavaScript, WebRTC

Backend (Server)

Manages routing, user sessions, and is the host for the CV pipeline.

Python (Flask)

CV Engine

Performs face detection, alignment, feature extraction, and matching.

OpenCV, face_recognition (dlib/CNN models), NumPy

Data Storage

Stores user credentials and facial embeddings.

Firebase/Firestore (as required by environment)

⚙️ Project Setup and Installation

Follow these steps to set up and run the project locally.

Prerequisites

Python 3.8+

pip (Python package installer)

A modern web browser with webcam access (WebRTC support).

Step 1: Clone the Repository

git clone [YOUR_REPOSITORY_URL]
cd real-time-face-recognition


Step 2: Set up the Python Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate


Step 3: Install Dependencies

The core CV libraries (dlib, face_recognition, OpenCV) can be heavy and sometimes complex to install.

pip install -r requirements.txt


(Note: You will need to create a requirements.txt containing the necessary packages like Flask, opencv-python, face-recognition, numpy, etc.)

Step 4: Configure Environment Variables

The application requires configuration details for the database and authentication.

Create a file named .env in the root directory.

Add your Firebase/Firestore configuration details (or local database configuration if adapting).

# --- FIREBASE/CANVAS CONFIGURATION (Mandatory for this environment) ---
APP_ID="[Provided App ID]"
FIREBASE_CONFIG='{"apiKey": "...", "authDomain": "...", ...}'
INITIAL_AUTH_TOKEN="[Provided Initial Auth Token]"

# --- FLASK CONFIGURATION ---
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY="YOUR_SUPER_SECRET_KEY"


Step 5: Initialize the Database (Firestore Logic)

In this implementation, the database is initialized within the client-side JavaScript using environment variables passed from the server. Ensure that your Firestore security rules are correctly configured to allow authenticated read/write access to the required collection paths (/artifacts/{appId}/users/{userId}/...).

Step 6: Run the Flask Application

Start the backend server:

flask run


The application will typically start on http://127.0.0.1:5000.

🖥️ Usage

Access the Application: Open your browser and navigate to the local server address (e.g., http://127.0.0.1:5000).

Registration: The system must first enroll a user.

Navigate to the registration page.

Input a username and capture multiple clear images of your face via the webcam.

The system will generate and securely store the facial embedding.

Verification:

Navigate to the verification page.

The system will compare your live feed against the stored embedding, performing liveness checks simultaneously.

Successful verification grants access, while failure will prompt for a retry or alternative authentication.

🛠️ Development & Contributions

Contributions are welcome! If you find a bug or have an idea for an enhancement (e.g., adding a custom deep learning model, improving liveness detection), please open an issue or submit a pull request.
