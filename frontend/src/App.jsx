import { useState } from "react";
import "./App.css";

const BACKEND_URL = "http://127.0.0.1:5000";

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleImageChange = (event) => {
    const file = event.target.files[0];

    if (!file) return;

    setSelectedImage(file);
    setPreview(URL.createObjectURL(file));
    setResults([]);
    setError("");
  };

  const searchProducts = async () => {
    if (!selectedImage) return;

    setLoading(true);
    setError("");
    setResults([]);

    const formData = new FormData();
    formData.append("image", selectedImage);

    try {
      const response = await fetch(`${BACKEND_URL}/search`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Search failed");
      }

      setResults(data.results || []);
    } catch {
      setError(
        "Search failed. Make sure the Flask backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <div className="hero">
          <p className="badge">AI PRODUCT SEARCH</p>

          <h1>
            Find Products
            <span> Like Your Image</span>
          </h1>

          <p className="subtitle">
            Upload a product image and discover visually similar products.
          </p>
        </div>

        <div className="upload-card">
          <div className="upload-box">
            {preview ? (
              <img
                src={preview}
                alt="Selected product"
                className="preview-image"
              />
            ) : (
              <>
                <div className="upload-icon">↑</div>

                <h2>Upload Product Image</h2>

                <p>PNG, JPG or JPEG</p>
              </>
            )}

            <label className="upload-button">
              {preview ? "Choose Another Image" : "Choose Image"}

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
              ? "🔄 Finding Similar Products..."
              : "🔍 Search Similar Products"}
          </button>

          {error && <p className="error-message">{error}</p>}
        </div>

        <div className="results">
          <h2>Similar Products</h2>

          {results.length === 0 && !loading && (
            <p className="empty-text">
              Upload an image to see matching products here.
            </p>
          )}

          <div className="results-grid">
            {results.map((product) => (
              <div className="product-card" key={product.image}>
                <img
                  src={`${BACKEND_URL}${product.image}`}
                  alt={product.name}
                />

                <div className="product-info">
                  <h3>{product.name}</h3>

                  <p>{product.similarity}% similarity</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;