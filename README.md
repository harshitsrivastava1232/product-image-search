# Product Image Search

An AI-powered image similarity search application that finds visually similar products from an uploaded image.

## Features

- Upload a product image
- Automatically identify the product category
- Compare products using deep-learning image features
- Rank products using cosine similarity
- Display the top visually similar products
- Responsive and modern React interface

## Product Categories

The dataset currently includes:

- Shoes
- Bags
- Watches
- Headphones
- Phones
- Laptops
- Sunglasses
- Bottles
- Hats
- Earphones

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

1. The user uploads a product image.
2. The Flask backend receives the image.
3. MobileNetV2 extracts visual features from the image.
4. The system determines the closest product category.
5. Products from unrelated categories are filtered out.
6. Cosine similarity is used to rank visually similar products.
7. The top matching products are displayed in the React interface.

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