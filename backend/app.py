from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import numpy as np
import os

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.models import Model


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
DATASET_FOLDER = "dataset"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)


# --------------------------------------------------
# AI MODEL
# --------------------------------------------------

base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    pooling="avg"
)

feature_model = Model(
    inputs=base_model.input,
    outputs=base_model.output
)


# --------------------------------------------------
# PRODUCT CATEGORIES
# --------------------------------------------------

CATEGORY_MAP = {
    "shoe": "shoes",
    "shoes": "shoes",

    "bag": "bags",
    "backpack": "bags",

    "watch": "watches",

    "headphone": "headphones",
    "headphones": "headphones",

    "phone": "phones",
    "smartphone": "phones",

    "laptop": "laptops",
    "notebook": "laptops",

    "sunglasses": "sunglasses",
    "glasses": "sunglasses",

    "bottle": "bottles",
    "water_bottle": "bottles",

    "hat": "hats",
    "cap": "hats",

    "earphone": "earphones",
    "earphones": "earphones",
    "earbud": "earphones",
    "earbuds": "earphones",
}


def get_category(filename):
    name = os.path.splitext(filename)[0].lower()

    for key, category in CATEGORY_MAP.items():
        if name.startswith(key):
            return category

    return None


# --------------------------------------------------
# IMAGE FEATURE EXTRACTION
# --------------------------------------------------

def extract_features(image_path):

    img = Image.open(image_path).convert("RGB")
    img = img.resize((224, 224))

    arr = keras_image.img_to_array(img)
    arr = np.expand_dims(arr, axis=0)
    arr = preprocess_input(arr)

    features = feature_model.predict(
        arr,
        verbose=0
    )[0]

    norm = np.linalg.norm(features)

    if norm == 0:
        return features

    return features / norm


def cosine_similarity(a, b):
    return float(np.dot(a, b))


# --------------------------------------------------
# DATASET CACHE
# --------------------------------------------------

DATASET_CACHE = []
CATEGORY_PROTOTYPES = {}


def load_dataset_cache():

    global DATASET_CACHE
    global CATEGORY_PROTOTYPES

    if DATASET_CACHE:
        return

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    }

    category_vectors = {}

    print("Loading dataset features...")

    for filename in os.listdir(DATASET_FOLDER):

        file_path = os.path.join(
            DATASET_FOLDER,
            filename
        )

        if not os.path.isfile(file_path):
            continue

        extension = os.path.splitext(
            filename
        )[1].lower()

        if extension not in allowed_extensions:
            continue

        category = get_category(filename)

        if not category:
            continue

        try:

            vector = extract_features(
                file_path
            )

            item = {
                "name": os.path.splitext(filename)[0],
                "image": f"/dataset/{filename}",
                "category": category,
                "features": vector
            }

            DATASET_CACHE.append(item)

            if category not in category_vectors:
                category_vectors[category] = []

            category_vectors[category].append(
                vector
            )

        except Exception as error:
            print(
                f"Skipping {filename}: {error}"
            )

    # Create one prototype vector for each category
    for category, vectors in category_vectors.items():

        prototype = np.mean(
            vectors,
            axis=0
        )

        norm = np.linalg.norm(prototype)

        if norm != 0:
            prototype = prototype / norm

        CATEGORY_PROTOTYPES[category] = prototype

    print(
        f"Dataset loaded: {len(DATASET_CACHE)} images"
    )

    print(
        f"Categories loaded: {list(CATEGORY_PROTOTYPES.keys())}"
    )


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():

    return {
        "message": "Product Image Search AI Backend is running"
    }


# --------------------------------------------------
# SEARCH
# --------------------------------------------------

@app.route("/search", methods=["POST"])
def search_products():

    if "image" not in request.files:

        return jsonify({
            "error": "No image uploaded"
        }), 400

    uploaded_file = request.files["image"]

    if uploaded_file.filename == "":

        return jsonify({
            "error": "No image selected"
        }), 400

    upload_path = os.path.join(
        UPLOAD_FOLDER,
        uploaded_file.filename
    )

    uploaded_file.save(
        upload_path
    )

    try:

        # Load dataset only once
        load_dataset_cache()

        if not DATASET_CACHE:

            return jsonify({
                "error": "Dataset is empty"
            }), 400

        # Extract uploaded image features
        query_features = extract_features(
            upload_path
        )

        # ------------------------------------------
        # Detect closest category
        # ------------------------------------------

        category_scores = []

        for category, prototype in CATEGORY_PROTOTYPES.items():

            score = cosine_similarity(
                query_features,
                prototype
            )

            category_scores.append({
                "category": category,
                "score": score
            })

        category_scores.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        selected_category = category_scores[0]["category"]

        # ------------------------------------------
        # Compare ONLY selected category
        # ------------------------------------------

        results = []

        for item in DATASET_CACHE:

            if item["category"] != selected_category:
                continue

            similarity = cosine_similarity(
                query_features,
                item["features"]
            )

            results.append({
                "name": item["name"],
                "image": item["image"],
                "category": item["category"],
                "similarity": round(
                    similarity * 100,
                    2
                )
            })

        results.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return jsonify({
            "category": selected_category,
            "results": results[:5]
        })

    except Exception as error:

        print("Search error:", error)

        return jsonify({
            "error": str(error)
        }), 500


# --------------------------------------------------
# DATASET IMAGES
# --------------------------------------------------

@app.route("/dataset/<path:filename>")
def dataset_file(filename):

    return send_from_directory(
        DATASET_FOLDER,
        filename
    )


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )