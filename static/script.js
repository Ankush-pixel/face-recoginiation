let currentImageTarget = null;
let videoStream;
let capturedImages = [];
let uploadedImages = [];

function startCamera(target) {
    currentImageTarget = target;
    const video = document.getElementById('camera-feed');
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            videoStream = stream;
            video.srcObject = stream;
            video.play();
            document.getElementById('camera-modal').style.display = 'block';
        })
        .catch(err => {
            console.error("Error accessing camera: ", err);
            alert("Error accessing camera: " + err.message);
        });
}

function capturePhoto() {
    const video = document.getElementById('camera-feed');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/png');

    if (currentImageTarget === 1 || currentImageTarget === 2) {
        const inputId = `file${currentImageTarget}`;
        const previewId = `dialog-preview${currentImageTarget}`;
        const imgPreview = document.getElementById(previewId);
        imgPreview.src = imageData;
        imgPreview.style.display = "block";

        fetch(imageData)
            .then(res => res.blob())
            .then(blob => {
                const file = new File([blob], `captured_${currentImageTarget}.png`, { type: "image/png" });
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                document.getElementById(inputId).files = dataTransfer.files;
                alert(`📸 Image captured and assigned to Image ${currentImageTarget}`);
            });
    }

    fetch('/save-image', {
        method: 'POST',
        body: JSON.stringify({ image: imageData }),
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        capturedImages.push(imageData);
        displayCapturedImages();
    })
    .catch(error => console.error("Error saving image:", error));

    closeCamera();
}

function closeCamera() {
    const video = document.getElementById('camera-feed');
    video.srcObject = null;
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
    }
    document.getElementById('camera-modal').style.display = 'none';
    alert("Camera has been closed.");
}

function previewImage(event, previewId) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        uploadedImages.push(e.target.result);
        const img = document.getElementById(previewId);
        if (img) {
            img.src = e.target.result;
            img.style.display = "block";
        }
        alert("🖼️ Image uploaded successfully!");
    };
    reader.readAsDataURL(file);
}

function displayCapturedImages() {
    const container = document.getElementById("capturedImagesContainer");
    if (!container) return;

    container.innerHTML = '';

    [...capturedImages, ...uploadedImages].forEach((src, index) => {
        const img = document.createElement('img');
        img.src = src;
        img.style.width = '100px';
        img.alt = `Image ${index + 1}`;
        container.appendChild(img);
    });

    fetch('/get-captured-images')
        .then(res => res.json())
        .then(data => {
            (data.images || []).forEach((src, i) => {
                const img = document.createElement('img');
                img.src = src;
                img.style.width = '100px';
                img.alt = `Server Image ${i + 1}`;
                container.appendChild(img);
            });
        })
        .catch(err => console.error("Error fetching server images:", err));
}

function showPreview() {
    const file1 = document.getElementById("file1").files[0];
    const file2 = document.getElementById("file2").files[0];
    const dialog = document.getElementById("image-preview-dialog");

    if (!file1 || !file2) {
        alert("⚠️ Please select or capture both images for preview!");
        return;
    }

    const reader1 = new FileReader();
    reader1.onload = () => {
        document.getElementById("dialog-preview1").src = reader1.result;
        document.getElementById("dialog-preview1").style.display = "block";
    };
    reader1.readAsDataURL(file1);

    const reader2 = new FileReader();
    reader2.onload = () => {
        document.getElementById("dialog-preview2").src = reader2.result;
        document.getElementById("dialog-preview2").style.display = "block";
    };
    reader2.readAsDataURL(file2);

    dialog.style.display = "block";
}

function closePreview() {
    document.getElementById("image-preview-dialog").style.display = "none";
}

function showSpeed() {
    const speedText = document.getElementById("network-speed-text");
    speedText.innerText = "Calculating speed...";
    fetch("/get-download-speed")
        .then(res => res.json())
        .then(data => {
            speedText.innerText = `Download Speed: ${data.download_speed} Mbps`;
        })
        .catch(err => {
            speedText.innerText = "⚠️ Error measuring speed!";
            console.error(err);
        });
}

function deleteImages() {
    if (capturedImages.length === 0 && uploadedImages.length === 0) {
        alert("No images to delete.");
        return;
    }

    fetch('/delete', {
        method: 'DELETE'
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || "Images deleted successfully!");
        capturedImages = [];
        uploadedImages = [];
        displayCapturedImages();
    })
    .catch(err => {
        console.error("Error deleting images:", err);
        alert("Error deleting images!");
    });
}

function showLoader() {
    document.getElementById("loader").style.display = "flex";
    document.getElementById("progress-bar-container").style.display = "block";

    let progress = 0;
    const progressText = document.getElementById("progress-text");
    const progressBar = document.getElementById("progress-bar");

    const interval = setInterval(() => {
        progress += 5;
        if (progress >= 100) {
            clearInterval(interval);
        }
        progressBar.style.width = `${progress}%`;
        progressText.innerText = `Processing... ${progress}%`;
    }, 500);
}

function hideLoader() {
    document.getElementById("loader").style.display = "none";
    document.getElementById("progress-bar-container").style.display = "none";
}

function showProcessingDialog() {
    document.getElementById("processing-dialog").style.display = "block";
}

function updateProcessingStep(step) {
    const steps = {
        age: "step-age",
        gender: "step-gender",
        emotion: "step-emotion"
    };
    const stepElement = document.getElementById(steps[step]);
    if (stepElement) {
        stepElement.innerHTML = `✅ ${step.charAt(0).toUpperCase() + step.slice(1)} Detected`;
        stepElement.style.color = "green";
    }

    if (step === "emotion") {
        document.getElementById("close-processing").style.display = "block";
    }
}

function closeProcessingDialog() {
    document.getElementById("processing-dialog").style.display = "none";
}

// Form submission with face comparison
document.getElementById("faceCompareForm").addEventListener("submit", function (event) {
    event.preventDefault();
    showLoader();
    showProcessingDialog();

    const formData = new FormData(this);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        hideLoader();
        updateProcessingStep("age");
        setTimeout(() => updateProcessingStep("gender"), 2000);
        setTimeout(() => updateProcessingStep("emotion"), 4000);
        setTimeout(() => {
            alert(data.message || "✅ Face comparison complete!");
            closeProcessingDialog();
            this.submit(); // Final form submission
        }, 6000);
    })
    .catch(error => {
        hideLoader();
        closeProcessingDialog();
        console.error("Error:", error);
        alert("Something went wrong!");
    });
});

document.addEventListener('keydown', e => {
    if (e.key === 'q') capturePhoto();
});

// Event listeners
document.addEventListener("DOMContentLoaded", displayCapturedImages);
document.getElementById("stop-camera-button").addEventListener("click", closeCamera);
document.getElementById("preview-button").addEventListener("click", showPreview);
