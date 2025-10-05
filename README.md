# 🏢 Dubai Real Estate Price Predictor

AI-powered property price prediction model for Dubai real estate market using Machine Learning.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 🎯 Features

- **Smart Dynamic Form**: Adaptive form fields based on property type and usage
- **Price Range Prediction**: Get price ranges (±10%) instead of single estimates
- **Location Premium**: Automatic adjustments for luxury areas (Palm Jumeirah, Burj Khalifa, etc.)
- **Validation Rules**: Built from 1.5M historical transactions (2000-2025)
- **Auto-fill Size**: Automatically suggests property size based on bedroom count
- **Batch Prediction**: Upload CSV to predict multiple properties at once

## 📊 Model Performance

- **R² Score**: 86.89% (test data)
- **Mean Absolute Error**: 247K AED
- **MAPE**: 16.69%
- **Training Data**: 188,185 transactions from 2025

## 🚀 Quick Start

### Local Deployment

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/dubai-real-estate-predictor.git
cd dubai-real-estate-predictor
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the Streamlit app**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### FastAPI Backend (Optional)

```bash
python start_api.py
```

API will be available at `http://localhost:8000/docs`

## ☁️ Streamlit Cloud Deployment

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/dubai-real-estate-predictor.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Important Notes**
   - Model files (`.pkl`) and JSON rules are included in the repo
   - Data files are excluded (add via `.gitignore`)
   - Config file (`.streamlit/config.toml`) is included for theming

## 📁 Project Structure

```
dubai-real-estate-predictor/
├── app.py                           # Main Streamlit application
├── api.py                           # FastAPI backend
├── requirements.txt                 # Python dependencies
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── model/
│   ├── random_forest_model.pkl     # Trained ML model
│   ├── label_encoder_*.pkl         # Feature encoders
│   ├── metadata.pkl                # Model metadata
│   ├── validation_rules.json       # Size ranges, property rules
│   ├── dynamic_form_rules.json     # Form field dependencies
│   ├── property_categorization.json # Residential/Commercial types
│   └── location_multipliers.json   # Premium pricing by area
├── analyze_property_hierarchy.py   # Data analysis script
├── calculate_location_premiums.py  # Calculate area premiums
├── clean_duplicate_areas.py        # Data cleaning
├── save_model.py                   # Model training & saving
└── test_model_performance.py       # Model evaluation
```

## 🔧 How It Works

### 1. Dynamic Form
- **Property Usage**: Residential, Commercial, etc.
- **Property Type**: Unit, Villa, Land, Building
- **Conditional Fields**: Bedrooms only shown for Units/Villas
- **Auto-fill**: Size automatically suggested based on bedroom count

### 2. Price Prediction
- Base prediction from Random Forest model
- Location multiplier applied:
  - **Ultra Luxury (2.0x)**: Jumeirah Second, Bluewaters, Trade Center
  - **Luxury (1.5x)**: Palm Jumeirah, Burj Khalifa, Palm Deira
  - **Premium (1.2x)**: Dubai Marina, Business Bay
  - **Average (1.0x)**: Standard areas
  - **Budget (0.9x)**: Emerging areas

### 3. Validation
- Size ranges by bedroom count (from 1.5M transactions)
- Property type constraints (e.g., Land cannot have bedrooms)
- Warnings for unusual inputs

## 📈 Key Features

| Feature | Importance |
|---------|-----------|
| Property Size | 66.2% |
| Location | 22.7% |
| Registration Type | 5.1% |
| Property Type | 2.4% |
| Bedrooms | 1.5% |
| Named Project | 1.3% |
| Parking | 0.7% |

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI (optional)
- **ML Model**: Random Forest Regressor (scikit-learn)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly

## 📝 API Usage

### Single Prediction

```bash
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

## 📊 Data Sources

- **Training Data**: Dubai Land Department 2025 transactions (188,185 records)
- **Validation Rules**: Historical data 2000-2024 (1.5M transactions)
- **Location Premiums**: Calculated from median price/sqm by area

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use for personal or commercial projects

## 👤 Author

Built with ❤️ for Dubai real estate market analysis

## 🐛 Issues

Report issues on [GitHub Issues](https://github.com/yourusername/dubai-real-estate-predictor/issues)

---

**Note**: Price predictions are estimates based on historical data and should not be used as the sole basis for real estate decisions. Always consult with real estate professionals.
