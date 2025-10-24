# 🚀 Dubai Real Estate Price Prediction API

FastAPI backend for Dubai real estate price prediction using Random Forest model.

## 📋 Features

- **REST API**: FastAPI with automatic OpenAPI documentation
- **Single Prediction**: POST endpoint for individual property predictions
- **Batch Prediction**: POST endpoint for bulk predictions
- **Location Premiums**: Automatic adjustments for luxury areas
- **Validation**: Input validation with warnings for unusual values
- **Full Model**: Uses uncompressed 181 MB Random Forest model (100 estimators)

## 📊 Model Performance

- **R² Score**: 86.89%
- **Mean Absolute Error**: 247K AED
- **MAPE**: 16.69%
- **Training Data**: 188,185 transactions from 2025

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone -b api-only https://github.com/utkarshkr100/mpp2.git
cd mpp2
```

### 2. Download Model File

⚠️ **Important**: The `random_forest_model.pkl` file (181 MB) is NOT in Git.

Download it separately:

```bash
# Download from Azure Storage (get URL from maintainer)
curl -o model/random_forest_model.pkl YOUR_MODEL_DOWNLOAD_URL
```

See [MODEL_SETUP.md](MODEL_SETUP.md) for detailed instructions.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the API Server

```bash
# Using start script
python start_api.py

# Or directly with uvicorn
uvicorn api:app --reload --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative docs)

## 📡 API Endpoints

### 1. Health Check

```bash
GET /
```

**Response:**
```json
{
  "message": "Dubai Real Estate Price Prediction API",
  "status": "running",
  "model_type": "RandomForestRegressor"
}
```

### 2. Model Info

```bash
GET /model-info
```

**Response:**
```json
{
  "model_type": "RandomForestRegressor",
  "training_samples": 150548,
  "r2_score": 0.8689,
  "mae": 247235.5,
  "features": ["procedure_area", "bedrooms", "has_parking", "has_project", "area_name_en", "property_sub_type_en", "reg_type_en"],
  "available_areas": 266,
  "available_property_types": 6,
  "available_registration_types": 2
}
```

### 3. Get Available Options

```bash
GET /options
```

**Response:**
```json
{
  "areas": ["BUSINESS BAY", "DUBAI MARINA", "PALM JUMEIRAH", ...],
  "property_subtypes": ["Flat", "Villa", "Hotel Apartment", ...],
  "registration_types": ["Off-Plan Properties", "Ready Properties"]
}
```

### 4. Single Prediction

```bash
POST /predict
```

**Request Body:**
```json
{
  "property_usage": "Residential",
  "property_type": "Unit",
  "property_subtype": "Flat",
  "area_size": 100,
  "bedrooms": 2,
  "has_parking": 1,
  "area_name": "DUBAI MARINA",
  "reg_type": "Off-Plan Properties"
}
```

**Response:**
```json
{
  "predicted_price": 1750000,
  "price_per_sqm": 17500,
  "location_multiplier": 1.2,
  "location_tier": "Premium",
  "confidence_level": "High",
  "validation_warnings": [],
  "input_summary": {
    "property_usage": "Residential",
    "property_type": "Unit",
    "property_subtype": "Flat",
    "area_size": 100,
    "bedrooms": 2,
    "location": "DUBAI MARINA"
  }
}
```

### 5. Batch Prediction

```bash
POST /predict-batch
```

**Request Body:**
```json
{
  "properties": [
    {
      "property_usage": "Residential",
      "property_type": "Unit",
      "property_subtype": "Flat",
      "area_size": 100,
      "bedrooms": 2,
      "has_parking": 1,
      "area_name": "DUBAI MARINA",
      "reg_type": "Off-Plan Properties"
    },
    {
      "property_usage": "Residential",
      "property_type": "Villa",
      "property_subtype": "Villa",
      "area_size": 300,
      "bedrooms": 4,
      "has_parking": 1,
      "area_name": "PALM JUMEIRAH",
      "reg_type": "Ready Properties"
    }
  ]
}
```

**Response:**
```json
{
  "predictions": [
    {
      "predicted_price": 1750000,
      "price_per_sqm": 17500,
      "location_multiplier": 1.2,
      "confidence_level": "High"
    },
    {
      "predicted_price": 8500000,
      "price_per_sqm": 28333,
      "location_multiplier": 1.5,
      "confidence_level": "Medium"
    }
  ],
  "summary": {
    "total_properties": 2,
    "average_price": 5125000,
    "total_value": 10250000
  }
}
```

## 🔧 Example Usage

### cURL

```bash
# Single prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "property_usage": "Residential",
    "property_type": "Unit",
    "property_subtype": "Flat",
    "area_size": 100,
    "bedrooms": 2,
    "has_parking": 1,
    "area_name": "DUBAI MARINA",
    "reg_type": "Off-Plan Properties"
  }'
```

### Python

```python
import requests

# Single prediction
url = "http://localhost:8000/predict"
payload = {
    "property_usage": "Residential",
    "property_type": "Unit",
    "property_subtype": "Flat",
    "area_size": 100,
    "bedrooms": 2,
    "has_parking": 1,
    "area_name": "DUBAI MARINA",
    "reg_type": "Off-Plan Properties"
}

response = requests.post(url, json=payload)
print(response.json())
```

### JavaScript

```javascript
// Single prediction
fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    property_usage: "Residential",
    property_type: "Unit",
    property_subtype: "Flat",
    area_size: 100,
    bedrooms: 2,
    has_parking: 1,
    area_name: "DUBAI MARINA",
    reg_type: "Off-Plan Properties"
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 📁 Project Structure

```
api-only/
├── api.py                          # FastAPI application
├── start_api.py                    # API launcher script
├── requirements.txt                # Python dependencies
├── model/
│   ├── random_forest_model.pkl    # Trained model (181 MB)
│   ├── label_encoder_*.pkl        # Feature encoders
│   ├── metadata.pkl               # Model metadata
│   ├── validation_rules.json      # Input validation rules
│   ├── dynamic_form_rules.json    # Property type rules
│   ├── property_categorization.json # Property categories
│   └── location_multipliers.json  # Premium pricing by area
└── README.md                       # This file
```

## 🎯 Location Multipliers

The API applies location-based premium multipliers:

- **Ultra Luxury (2.0x)**: Jumeirah Second, Bluewaters, Trade Center
- **Luxury (1.5x)**: Palm Jumeirah, Burj Khalifa, Palm Deira
- **Premium (1.2x)**: Dubai Marina, Business Bay, JBR
- **Average (1.0x)**: Standard areas
- **Budget (0.9x)**: Emerging areas

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **ML Model**: Random Forest Regressor (scikit-learn)
- **Server**: Uvicorn
- **Data Processing**: Pandas, NumPy
- **Validation**: Pydantic

## 📝 Environment Variables

Optional environment variables:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS (default: allow all)
CORS_ORIGINS=*
```

## 🚀 Deployment

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

This API can be deployed to:
- **Heroku**: Add `Procfile` with `web: uvicorn api:app --host 0.0.0.0 --port $PORT`
- **AWS Lambda**: Use Mangum adapter
- **Google Cloud Run**: Use Docker container
- **Azure App Service**: Direct Python deployment

## ⚠️ Important Notes

- **Model Size**: This branch uses the full 181 MB model (not compressed)
- **Git LFS Required**: For GitHub push, use Git LFS for large files
- **No UI**: This is API-only; for UI, use the `master` branch
- **Performance**: Full model provides better accuracy (86.9% R²)

## 📊 Model Details

- **Algorithm**: Random Forest with 100 estimators
- **Max Depth**: 20
- **Features**: 7 (size, bedrooms, parking, project, area, property type, registration type)
- **Training Size**: 150,548 properties
- **Test Size**: 37,637 properties

## 🤝 Related Branches

- **master**: Streamlit UI with compressed model (54 MB)
- **api-only**: FastAPI with full model (181 MB) - This branch

## 📄 License

MIT License

## 👤 Author

Dubai Real Estate ML Project
