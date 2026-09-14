from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import numpy as np
import os

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import (
    preprocess_input,
    decode_predictions,
)
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.models import Model


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
DATASET_FOLDER = "dataset"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)

# Pre-trained CNN model for image feature extraction
base_model = MobileNetV2(weights="imagenet", include_top=True)

# Use the layer before final classification
feature_model = Model(
    inputs=base_model.input,
    outputs=base_model.layers[-2].output
)


def extract_features(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((224, 224))

    img_array = keras_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    features = feature_model.predict(img_array, verbose=0)[0]

    # Normalize feature vector
    norm = np.linalg.norm(features)

    if norm == 0:
        return features

    return features / norm


def cosine_similarity(vector_a, vector_b):
    return float(np.dot(vector_a, vector_b))


@app.route("/")
def home():
    return {
        "message": "Product Image Search AI Backend is running"
    }


@app.route("/search", methods=["POST"])
def search_products():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    uploaded_file = request.files["image"]

    if uploaded_file.filename == "":
        return jsonify({"error": "No image selected"}), 400

    upload_path = os.path.join(
        UPLOAD_FOLDER,
        uploaded_file.filename
    )

    uploaded_file.save(upload_path)

    try:
        query_features = extract_features(upload_path)

        results = []

        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}

        for filename in os.listdir(DATASET_FOLDER):

            file_path = os.path.join(DATASET_FOLDER, filename)

            if not os.path.isfile(file_path):
                continue

            extension = os.path.splitext(filename)[1].lower()

            if extension not in allowed_extensions:
                continue

            try:
                product_features = extract_features(file_path)

                similarity = cosine_similarity(
                    query_features,
                    product_features
                )

                results.append({
                    "name": os.path.splitext(filename)[0],
                    "image": f"/dataset/{filename}",
                    "similarity": round(similarity * 100, 2),
                })

            except Exception:
                continue

        results.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return jsonify({
            "results": results[:5]
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


@app.route("/dataset/<path:filename>")
def dataset_file(filename):
    return send_from_directory(DATASET_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
    