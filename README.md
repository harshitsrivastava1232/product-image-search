# Product Image Search

An AI-powered image similarity search application that finds visually similar products from an uploaded image.

## Features

- Upload a product image
- Extract image features using MobileNetV2
- Compare images using cosine similarity
- Display top 5 visually similar products
- Responsive React user interface

## Tech Stack

### Frontend
- React.js
- Vite
- CSS

### Backend
- Python
- Flask
- Flask-CORS

### AI/ML
- TensorFlow
- Keras
- MobileNetV2
- NumPy
- Pillow

## How It Works

1. User uploads a product image.
2. React sends the image to the Flask backend.
3. MobileNetV2 extracts image features.
4. The feature vector is compared with product images in the dataset.
5. Products are ranked using cosine similarity.
6. The top 5 matching products are displayed.

## Project Structure

```text
product-image-search/
│
├── backend/
│   ├── dataset/
│   ├── uploads/
│   └── app.py
│
├── frontend/
│   └── src/
│
├── .gitignore
└── README.md# Product Image Search

An AI-powered image similarity search application that finds visually similar products from an uploaded image.

## Features

- Upload a product image
- Extract image features using MobileNetV2
- Compare images using cosine similarity
- Display top 5 visually similar products
- Responsive React user interface

## Tech Stack

### Frontend
- React.js
- Vite
- CSS

### Backend
- Python
- Flask
- Flask-CORS

### AI/ML
- TensorFlow
- Keras
- MobileNetV2
- NumPy
- Pillow

## How It Works

1. User uploads a product image.
2. React sends the image to the Flask backend.
3. MobileNetV2 extracts image features.
4. The feature vector is compared with product images in the dataset.
5. Products are ranked using cosine similarity.
6. The top 5 matching products are displayed.

## Project Structure

```text
product-image-search/
│
├── backend/
│   ├── dataset/
│   ├── uploads/
│   └── app.py
│
├── frontend/
│   └── src/
│
├── .gitignore
└── README.md