import { useState } from "react";
import * as tf from "@tensorflow/tfjs";
import "@tensorflow/tfjs-backend-webgl";
import "@tensorflow/tfjs-backend-cpu";
import * as mobilenet from "@tensorflow-models/mobilenet";
import "./App.css";

const BACKEND_URL = import.meta.env.DEV
  ? "http://127.0.0.1:5000"
  : "https://product-image-search.onrender.com";

let mobileNetModel = null;

const detectCategory = (predictions) => {
  const categoryKeywords = {
    shoes: [
      "shoe",
      "sneaker",
      "running shoe",
      "running",
      "jersey",
      "clog",
    ],
    bags: [
      "bag",
      "backpack",
      "purse",
      "pouch",
      "briefcase",
      "wallet",
    ],
    watches: [
      "watch",
      "analog clock",
      "digital watch",
      "stopwatch",
    ],
    headphones: [
      "headphone",
      "headset",
      "earphone",
    ],
    phones: [
      "cellular telephone",
      "cellular phone",
      "mobile phone",
      "smartphone",
      "telephone",
    ],
    laptops: [
      "laptop",
      "notebook",
      "computer",
    ],
    sunglasses: [
      "sunglasses",
      "sunglass",
      "eyeglasses",
      "glasses",
    ],
    bottles: [
      "bottle",
      "water bottle",
      "beer bottle",
      "wine bottle",
    ],
    hats: [
      "hat",
      "cap",
      "cowboy hat",
      "sombrero",
      "bonnet",
    ],
    earphones: [
      "earphone",
      "earbud",
      "airpod",
      "headphone",
    ],
  };

  for (const prediction of predictions) {
    const label = prediction.className.toLowerCase();

    for (const [category, keywords] of Object.entries(categoryKeywords)) {
      if (keywords.some((keyword) => label.includes(keyword))) {
        return category;
      }
    }
  }

  return "";
};

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState([]);
  const [category, setCategory] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleImageChange = (event) => {
    const file = event.target.files[0];

    if (!file) return;

    setSelectedImage(file);
    setPreview(URL.createObjectURL(file));
    setResults([]);
    setCategory("");
    setError("");
  };

  const clearSearch = () => {
    setSelectedImage(null);
    setPreview(null);
    setResults([]);
    setCategory("");
    setError("");
  };

  const loadMobileNet = async () => {
  if (!mobileNetModel) {
    try {
      await tf.setBackend("webgl");
    } catch {
      await tf.setBackend("cpu");
    }

    await tf.ready();

    mobileNetModel = await mobilenet.load({
      version: 2,
      alpha: 1.0,
    });
  }

  return mobileNetModel;
};

  const getImageElement = (file) => {
    return new Promise((resolve, reject) => {
      const image = new Image();
      const url = URL.createObjectURL(file);

      image.onload = () => {
        URL.revokeObjectURL(url);
        resolve(image);
      };

      image.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error("Unable to load image"));
      };

      image.src = url;
    });
  };

  const searchProducts = async () => {
    if (!selectedImage) return;

    setLoading(true);
    setError("");
    setResults([]);

    try {
      // Load MobileNetV2 in browser
      const model = await loadMobileNet();

      // Convert uploaded file into image
      const imageElement = await getImageElement(selectedImage);

      // Get top MobileNet predictions
      const predictions = await model.classify(
        imageElement,
        5
      );

      console.log("MobileNet predictions:", predictions);

      // Detect one of our application categories
      const detectedCategory = detectCategory(predictions);

      console.log(
        "Detected category:",
        detectedCategory
      );

      const formData = new FormData();
      formData.append("image", selectedImage);

      if (detectedCategory) {
        formData.append(
          "category",
          detectedCategory
        );
      }

      const response = await fetch(
        `${BACKEND_URL}/search`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Search failed"
        );
      }

      setResults(data.results || []);
      setCategory(
        data.category ||
          detectedCategory ||
          ""
      );
    } catch (err) {
      console.error(err);

      setError(
        "Search failed. Please try another product image."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">

        <header className="hero">
          <div className="badge">
            AI PRODUCT SEARCH
          </div>

          <h1>
            Find Products
            <span> Like Your Image</span>
          </h1>

          <p className="subtitle">
            Upload any product image and discover
            visually similar products using
            AI-powered image matching.
          </p>
        </header>

        <section className="upload-card">

          <div className="upload-box">

            {preview ? (
              <>
                <div className="preview-wrapper">

                  <img
                    src={preview}
                    alt="Selected product"
                    className="preview-image"
                  />

                  <button
                    className="remove-button"
                    onClick={clearSearch}
                    type="button"
                  >
                    ×
                  </button>

                </div>

                <p className="selected-label">
                  Image selected successfully
                </p>
              </>
            ) : (
              <>
                <div className="upload-icon">
                  ↑
                </div>

                <h2>
                  Upload Product Image
                </h2>

                <p>
                  JPG, JPEG or PNG
                </p>
              </>
            )}

            <label className="upload-button">

              {preview
                ? "Choose Another Image"
                : "Choose Image"}

              <input
                type="file"
                accept="image/png,image/jpeg,image/jpg"
                onChange={handleImageChange}
              />

            </label>

          </div>

          <button
            className="search-button"
            disabled={!selectedImage || loading}
            onClick={searchProducts}
          >
            {loading
              ? "🔄 Analyzing Image..."
              : "🔍 Search Similar Products"}
          </button>

          {error && (
            <p className="error-message">
              {error}
            </p>
          )}

        </section>

        <section className="results">

          <div className="results-header">

            <div>
              <p className="section-label">
                SEARCH RESULTS
              </p>

              <h2>
                Similar Products
              </h2>
            </div>

            {category && (
              <div className="category-badge">
                {category}
              </div>
            )}

          </div>

          {loading && (
            <div className="loading-box">
              <div className="spinner"></div>

              <p>
                Finding the closest visual matches...
              </p>
            </div>
          )}

          {!loading &&
            results.length === 0 &&
            !error && (
              <div className="empty-state">

                <div className="empty-icon">
                  ✦
                </div>

                <h3>
                  No results yet
                </h3>

                <p>
                  Upload a product image to start
                  your AI search.
                </p>

              </div>
            )}

          {!loading &&
            results.length > 0 && (
              <div className="results-grid">

                {results.map((product) => (

                  <div
                    className="product-card"
                    key={product.image}
                  >

                    <div className="product-image-wrap">

                      <img
                        src={`${BACKEND_URL}${product.image}`}
                        alt={product.name}
                      />

                    </div>

                    <div className="product-info">

                      <h3>
                        {product.name.replaceAll(
                          "_",
                          " "
                        )}
                      </h3>

                      <div className="score-row">

                        <span>
                          Similarity
                        </span>

                        <strong>
                          {product.similarity}%
                        </strong>

                      </div>

                      <div className="score-track">

                        <div
                          className="score-fill"
                          style={{
                            width: `${Math.min(
                              product.similarity,
                              100
                            )}%`,
                          }}
                        ></div>

                      </div>

                    </div>

                  </div>

                ))}

              </div>
            )}

        </section>

      </div>
    </div>
  );
}

export default App;