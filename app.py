import os
import cv2
import numpy as np
import glob
import requests
import json
import speedtest
from flask import Flask, render_template, request, jsonify,send_from_directory
from deepface import DeepFace
import tensorflow as tf
from tensorflow.keras.models import load_model
import torch
import torchvision.transforms as transforms
from PIL import Image
from datetime import datetime
import base64
import time
torch.set_num_threads(1)  
os.environ["DEEPFACE_HOME"] = "C:\\Users\\ankus"
app = Flask(__name__)
UPLOAD_FOLDER = "static/upload"
PROCESSED_FOLDER = "static/processed"
DELETED_FOLDER="static/delete"
UPLOAD="static/images"
os.makedirs(UPLOAD, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(DELETED_FOLDER,exist_ok=True)
MODELS = ["ArcFace", "Facenet", "OpenFace", "DeepID"]

liveness_model = load_model("models/liveness_model.h5")  

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def cleanup_folder(folder):
    """Remove all files in a folder."""
    for file in glob.glob(os.path.join(folder, "*")):
        try:
            os.remove(file)
        except Exception as e:
            print(f"❌ Error deleting {file}: {e}")
def detect_faces_retinaface(image_path):
    """Detect multiple faces in an image using RetinaFace."""
    try:
        faces = DeepFace.extract_faces(image_path, detector_backend="retinaface", align=True)
        face_info = []
        for face in faces:
            facial_area = face.get('facial_area', {})
            face_info.append({
                'bbox': [
                    facial_area.get('x', 0),
                    facial_area.get('y', 0),
                    facial_area.get('x', 0) + facial_area.get('w', 0),
                    facial_area.get('y', 0) + facial_area.get('h', 0)
                ]
            })
        return len(faces), face_info
    except Exception as e:
        print(f"❌ Face Detection Error: {e}")
        return 0, []

def detect_spoof(image_path):
    """Detect spoof attacks using deep learning."""
    try:
        image = Image.open(image_path).convert('RGB')
        image=image.resize((64,64))
        image_np=np.array(image)/255.0
        image_np = np.expand_dims(image_np, axis=0)
        prediction = liveness_model.predict(image_np)[0]
        return prediction[0] > 0.5  
    except Exception as e:
        print(f"❌ Spoof Detection Error: {e}")
        return False

def process_verification(image1_path, image2_path, model_name):
    """Perform face verification using DeepFace."""
    try:
        spoof1 = detect_spoof(image1_path)
        spoof2 = detect_spoof(image2_path)
        spoof_warning = ""
        if not spoof1 and not spoof2:
            spoof_warning = "⚠️ Warning: Both images detected as  spoofs!"
        elif not spoof1:
            spoof_warning = "⚠️ Warning: First image detected as  spoof!"
        elif not spoof2:
            spoof_warning = "⚠️ Warning: Second image detected as spoof!"
        num_faces1, _ = detect_faces_retinaface(image1_path)
        if num_faces1 == 0:
            return None, "No face detected in first image. Please use a image.", None, None, None, None, None, None

        num_faces2, _ = detect_faces_retinaface(image2_path)
        if num_faces2 == 0:
            return None, "No face detected in second image. Please use a image.", None, None, None, None, None, None
        elif num_faces1==0 or num_faces2==0:
            return None, "No face detected in both Imges Please use a image.",None ,None,None,None,None,None
        attributes1 = DeepFace.analyze(
            img_path=image1_path,
            actions=['age', 'gender', 'race', 'emotion'],
            enforce_detection=True,
            detector_backend="retinaface"
        )[0]

        attributes2 = DeepFace.analyze(
            img_path=image2_path,
            actions=['age', 'gender', 'race', 'emotion'],
            enforce_detection=True,
            detector_backend="retinaface"
        )[0]

        age1, age2 = attributes1.get("age", "Unknown"), attributes2.get("age", "Unknown")
        gender1 = "Male" if attributes1["dominant_gender"] == "Man" else "Female"
        gender2 = "Male" if attributes2["dominant_gender"] == "Man" else "Female"
        emotion1, emotion2 = attributes1.get("dominant_emotion", "Unknown"), attributes2.get("dominant_emotion", "Unknown")

        result = DeepFace.verify(
            img1_path=image1_path,
            img2_path=image2_path,
            model_name=model_name,
            enforce_detection=True,
            detector_backend="retinaface",
        )
        similarity_score = round(result["distance"], 4)
        is_match = similarity_score < result["threshold"]
        match_result = "Yes" if is_match else "No"
        if spoof_warning:
            match_result = f"{match_result} ({spoof_warning})"

        return similarity_score, match_result, age1, age2, gender1, gender2, emotion1, emotion2,spoof1,spoof2

    except Exception as e:
        print(f"❌ DeepFace Error: {e}")
        return None, "DeepFace processing failed", None, None, None, None, None, None

def process_image(file):
    """Process and validate uploaded/captured image."""
    try:
        nparr = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return None, "Invalid image format"
            
        file.seek(0)
        

        if img.shape[0] < 100 or img.shape[1] < 100:
            return None, "Image too small. Minimum size is 100x100 pixels."
            
        return img, None
    except Exception as e:
        return None, f"Error processing image: {str(e)}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    cleanup_folder(UPLOAD_FOLDER)
    cleanup_folder(PROCESSED_FOLDER)

    if "image1" not in request.files or "image2" not in request.files or "model" not in request.form:
        return render_template("error.html", message="⚠️ Both images and a model selection are required!", button_text="Try Again", button_link="/"), 400

    selected_model = request.form["model"]
    if selected_model not in MODELS:
        return render_template("error.html", message="⚠️ Invalid model selection!", button_text="Try Again", button_link="/"), 400

    file1, file2 = request.files["image1"], request.files["image2"]
    img1, error1 = process_image(file1)
    if error1:
        return render_template("error.html", message=f"⚠️ Error with first image: {error1}", button_text="Try Again", button_link="/"), 400
        
    img2, error2 = process_image(file2)
    if error2:
        return render_template("error.html", message=f"⚠️ Error with second image: {error2}", button_text="Try Again", button_link="/"), 400
    timestamp=int(time.time())
    path1 = os.path.join(UPLOAD_FOLDER, f"face1_{timestamp}.jpg")
    path2 = os.path.join(UPLOAD_FOLDER, f"face2_{timestamp}.jpg")
    cv2.imwrite(path1, img1)
    cv2.imwrite(path2, img2)
    num_faces1, faces1 = detect_faces_retinaface(path1)
    num_faces2, faces2 = detect_faces_retinaface(path2)
    processed_path1 = os.path.join(PROCESSED_FOLDER, "processed_face1.jpg")
    processed_path2 = os.path.join(PROCESSED_FOLDER, "processed_face2.jpg")
    img1_with_rect = img1.copy()
    img2_with_rect = img2.copy()
    for i, face in enumerate(faces1):
        x1, y1, x2, y2 = [int(coord) for coord in face['bbox']]
        cv2.rectangle(img1_with_rect, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img1_with_rect, f"Face {i+1}", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    for i, face in enumerate(faces2):
        x1, y1, x2, y2 = [int(coord) for coord in face['bbox']]
        cv2.rectangle(img2_with_rect, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img2_with_rect, f"Face {i+1}", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    cv2.imwrite(processed_path1, img1_with_rect)
    cv2.imwrite(processed_path2, img2_with_rect)
    score, match, age1, age2, gender1, gender2, emotion1, emotion2 ,spoof1,spoof2= process_verification(path1, path2, selected_model)
    if score is None:
        return render_template("error.html", message=f"⚠️ Error: {match}", button_text="Try Again", button_link="/"), 400

    
    def img_to_base64(img_path):
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')

    img1_base64 = img_to_base64(processed_path1)
    img2_base64 = img_to_base64(processed_path2)

    if score is not None:
        confidence = score  # or any other value you want to use as confidence
        save_verification_history("user_identifier", path1, path2, match, confidence)  # Replace "user_identifier" with actual user info

    return render_template(
        "result.html",
        match={selected_model: match},
        scores={selected_model: score},
        img1_data=f"data:image/jpeg;base64,{img1_base64}",
        img2_data=f"data:image/jpeg;base64,{img2_base64}",
        num_faces1=num_faces1,
        num_faces2=num_faces2,
        selected_model=selected_model,
        age1=age1,
        age2=age2,
        gender1=gender1,
        gender2=gender2,
        emotion1=emotion1,
        emotion2=emotion2,
        spoof1=spoof1,
        spoof2=spoof2,
    )

@app.route('/get-download-speed', methods=['GET'])
def get_download_speed():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / (1024 * 1024)
        return jsonify({"download_speed": round(download_speed, 2)})
    except Exception as e:
        print(f"❌ Error measuring download speed: {e}")
        return jsonify({"error": "Failed to measure download speed"}), 500  
@app.route('/save-image', methods=['POST'])
def save_image():
    data = request.get_json()
    image_data = data.get('image')

    if image_data:
        header, encoded = image_data.split(',', 1)
        image_bytes = base64.b64decode(encoded)

        filename = os.path.join(UPLOAD, f'captured_image_{int(time.time())}.png')
        with open(filename, 'wb') as f:
            f.write(image_bytes)

        return jsonify({"message": "Image saved successfully!"}), 200
    return jsonify({"error": "No image data provided!"}), 400

@app.route('/delete', methods=['DELETE'])
def delete_images():
    try:
        for filename in os.listdir(UPLOAD):
            src = os.path.join(UPLOAD, filename)
            dst = os.path.join(DELETED_FOLDER, filename)
            os.rename(src, dst) 

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/get-captured-images', methods=['GET'])
def get_captured_images():
    try:
        image_files = [f for f in os.listdir(UPLOAD) if f.endswith(('.png', '.jpg', '.jpeg'))]

        image_urls = [f"/static/images/{img}?t={int(time.time())}" for img in image_files]

        return jsonify({"images": image_urls})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def save_verification_history(user, image1, image2, result, confidence):
    """Save verification history to a JSON file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "image1": image1,
        "image2": image2,
        "result": result,
        "confidence": confidence
    }

    try:
        with open("history.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(entry)

    try:
        with open("history.json", "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"❌ Error saving history: {e}")



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

