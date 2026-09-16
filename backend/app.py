from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import numpy as np
import os


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

USE_TENSORFLOW = (
    os.environ.get("USE_TENSORFLOW", "true").lower() == "true"
)


# --------------------------------------------------
# OPTIONAL AI MODEL
# --------------------------------------------------

if USE_TENSORFLOW:
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
    from tensorflow.keras.preprocessing import image as keras_image
    from tensorflow.keras.models import Model


# --------------------------------------------------
# FLASK APP
# --------------------------------------------------

app = Flask(__name__)
CORS(app)


# --------------------------------------------------
# FOLDERS
# --------------------------------------------------

UPLOAD_FOLDER = "uploads"
DATASET_FOLDER = "dataset"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)


# --------------------------------------------------
# AI MODEL
# --------------------------------------------------

feature_model = None

if USE_TENSORFLOW:

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
    "purse": "bags",

    "watch": "watches",
    "stopwatch": "watches",

    "headphone": "headphones",
    "headphones": "headphones",
    "headset": "headphones",

    "phone": "phones",
    "smartphone": "phones",
    "mobile": "phones",

    "laptop": "laptops",
    "notebook": "laptops",
    "computer": "laptops",

    "sunglasses": "sunglasses",
    "sunglass": "sunglasses",
    "glasses": "sunglasses",
    "eyeglasses": "sunglasses",

    "bottle": "bottles",
    "water bottle": "bottles",

    "hat": "hats",
    "cap": "hats",

    "earphone": "earphones",
    "earphones": "earphones",
    "earbud": "earphones",
    "earbuds": "earphones",
    "airpod": "earphones",
}


def normalize_category(category):
    """
    Convert different category names into
    our application's standard category names.
    """

    if not category:
        return ""

    category = category.lower().strip()

    return CATEGORY_MAP.get(
        category,
        category
    )


# --------------------------------------------------
# CATEGORY FROM DATASET FILENAME
# --------------------------------------------------

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


    # --------------------------------------------------
    # LOCAL MACHINE
    # MobileNetV2
    # --------------------------------------------------

    if USE_TENSORFLOW:

        img = img.resize((224, 224))

        arr = keras_image.img_to_array(img)

        arr = np.expand_dims(
            arr,
            axis=0
        )

        arr = preprocess_input(arr)

        features = feature_model.predict(
            arr,
            verbose=0
        )[0]

        norm = np.linalg.norm(features)

        if norm == 0:

            return features

        return features / norm


    # --------------------------------------------------
    # RENDER FREE TIER
    # Lightweight visual features
    # --------------------------------------------------

    img = img.resize((64, 64))

    arr = np.asarray(
        img,
        dtype=np.float32
    ) / 255.0


    # Average RGB color

    mean_color = arr.mean(
        axis=(0, 1)
    )


    # Color variation

    std_color = arr.std(
        axis=(0, 1)
    )


    # Grayscale

    gray = (
        0.299 * arr[:, :, 0]
        + 0.587 * arr[:, :, 1]
        + 0.114 * arr[:, :, 2]
    )


    # Horizontal edges

    horizontal_edges = np.abs(
        np.diff(
            gray,
            axis=1
        )
    ).mean(axis=0)


    # Vertical edges

    vertical_edges = np.abs(
        np.diff(
            gray,
            axis=0
        )
    ).mean(axis=1)


    # Resize edge vectors

    horizontal_edges = np.interp(
        np.linspace(
            0,
            len(horizontal_edges) - 1,
            32
        ),
        np.arange(
            len(horizontal_edges)
        ),
        horizontal_edges
    )


    vertical_edges = np.interp(
        np.linspace(
            0,
            len(vertical_edges) - 1,
            32
        ),
        np.arange(
            len(vertical_edges)
        ),
        vertical_edges
    )


    # Spatial brightness

    spatial = gray.reshape(
        8,
        8,
        8,
        8
    ).mean(
        axis=(1, 3)
    ).flatten()


    # Final feature vector

    features = np.concatenate([
        mean_color,
        std_color,
        horizontal_edges,
        vertical_edges,
        spatial
    ])


    # Normalize

    norm = np.linalg.norm(
        features
    )

    if norm == 0:

        return features

    return features / norm


# --------------------------------------------------
# COSINE SIMILARITY
# --------------------------------------------------

def cosine_similarity(a, b):

    return float(
        np.dot(a, b)
    )


# --------------------------------------------------
# DATASET CACHE
# --------------------------------------------------

DATASET_CACHE = []


def load_dataset_cache():

    global DATASET_CACHE

    if DATASET_CACHE:

        return


    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    }


    print("Loading dataset features...")


    for filename in os.listdir(
        DATASET_FOLDER
    ):

        file_path = os.path.join(
            DATASET_FOLDER,
            filename
        )


        if not os.path.isfile(
            file_path
        ):

            continue


        extension = os.path.splitext(
            filename
        )[1].lower()


        if extension not in allowed_extensions:

            continue


        category = get_category(
            filename
        )


        if not category:

            continue


        try:

            vector = extract_features(
                file_path
            )


            DATASET_CACHE.append({

                "name":
                    os.path.splitext(
                        filename
                    )[0],

                "image":
                    f"/dataset/{filename}",

                "category":
                    category,

                "features":
                    vector

            })


        except Exception as error:

            print(
                f"Skipping {filename}: {error}"
            )


    print(
        f"Dataset loaded: {len(DATASET_CACHE)} images"
    )


    categories = sorted(
        set(
            item["category"]
            for item in DATASET_CACHE
        )
    )


    print(
        f"Categories loaded: {categories}"
    )


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():

    return jsonify({

        "message":
            "Product Image Search AI Backend is running"

    })


# --------------------------------------------------
# SEARCH
# --------------------------------------------------

@app.route(
    "/search",
    methods=["POST"]
)
def search_products():

    # --------------------------------------------------
    # CHECK IMAGE
    # --------------------------------------------------

    if "image" not in request.files:

        return jsonify({

            "error":
                "No image uploaded"

        }), 400


    uploaded_file = request.files[
        "image"
    ]


    if uploaded_file.filename == "":

        return jsonify({

            "error":
                "No image selected"

        }), 400


    # --------------------------------------------------
    # SAVE UPLOADED IMAGE
    # --------------------------------------------------

    upload_path = os.path.join(
        UPLOAD_FOLDER,
        uploaded_file.filename
    )


    uploaded_file.save(
        upload_path
    )


    try:

        # --------------------------------------------------
        # LOAD DATASET
        # --------------------------------------------------

        load_dataset_cache()


        if not DATASET_CACHE:

            return jsonify({

                "error":
                    "Dataset is empty"

            }), 400


        # --------------------------------------------------
        # GET CATEGORY FROM FRONTEND
        # --------------------------------------------------

        requested_category = request.form.get(
            "category",
            ""
        )


        requested_category = normalize_category(
            requested_category
        )


        # --------------------------------------------------
        # EXTRACT QUERY FEATURES
        # --------------------------------------------------

        query_features = extract_features(
            upload_path
        )


        # --------------------------------------------------
        # DETERMINE SEARCH CATEGORY
        # --------------------------------------------------

        selected_category = ""


        # Use frontend MobileNet category
        # when it matches our dataset

        if requested_category:

            matching_items = [

                item
                for item in DATASET_CACHE
                if item["category"]
                == requested_category

            ]


            if matching_items:

                selected_category = (
                    requested_category
                )


        # --------------------------------------------------
        # FALLBACK CATEGORY DETECTION
        # --------------------------------------------------

        if not selected_category:

            best_match = max(

                DATASET_CACHE,

                key=lambda item:
                    cosine_similarity(

                        query_features,
                        item["features"]

                    )
            )


            selected_category = (
                best_match["category"]
            )


        # --------------------------------------------------
        # ONLY COMPARE PRODUCTS
        # INSIDE SELECTED CATEGORY
        # --------------------------------------------------

        results = []


        for item in DATASET_CACHE:

            if (
                item["category"]
                != selected_category
            ):

                continue


            similarity = cosine_similarity(

                query_features,
                item["features"]

            )


            results.append({

                "name":
                    item["name"],

                "image":
                    item["image"],

                "category":
                    item["category"],

                "similarity":
                    round(
                        similarity * 100,
                        2
                    )

            })


        # --------------------------------------------------
        # SORT RESULTS
        # --------------------------------------------------

        results.sort(

            key=lambda item:
                item["similarity"],

            reverse=True

        )


        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return jsonify({

            "category":
                selected_category,

            "results":
                results[:5]

        })


    except Exception as error:

        print(
            "Search error:",
            error
        )


        return jsonify({

            "error":
                str(error)

        }), 500


# --------------------------------------------------
# DATASET IMAGES
# --------------------------------------------------

@app.route(
    "/dataset/<path:filename>"
)
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