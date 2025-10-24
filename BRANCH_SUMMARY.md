# 🌳 Branch Structure Summary

This repository has two branches for different deployment scenarios.

## 📊 Branch Comparison

| Feature | `master` Branch | `api-only` Branch |
|---------|----------------|-------------------|
| **Purpose** | Streamlit UI App | FastAPI Backend Only |
| **Model File** | Compressed (54 MB) | Uncompressed (181 MB) |
| **Model In Git** | ✅ Yes (.pkl.gz) | ❌ No (too large) |
| **UI Included** | ✅ Streamlit App | ❌ No UI |
| **API Included** | ✅ FastAPI | ✅ FastAPI Only |
| **Dependencies** | Streamlit + FastAPI | FastAPI Only |
| **Model Performance** | 86.9% R² | 86.9% R² (same model) |
| **Deployment** | Streamlit Cloud | Azure/AWS/Docker |
| **File Size** | ~60 MB total | ~10 MB (without model) |
| **Model Storage** | In Git Repository | Azure Storage Account |

---

## 🎯 `master` Branch - Streamlit UI

### What's Included:
- ✅ **app.py** - Full Streamlit web interface
- ✅ **api.py** - FastAPI backend (optional)
- ✅ **Compressed model** - 54 MB (.pkl.gz)
- ✅ **All encoders** - Label encoders for features
- ✅ **Validation rules** - JSON files
- ✅ **Location multipliers** - Premium pricing
- ✅ **Configuration** - .streamlit/config.toml

### Use Cases:
- ✅ End-user web application
- ✅ Interactive price predictions
- ✅ Batch CSV upload
- ✅ Data visualization
- ✅ Demo and testing

### Deployment:
```bash
# Clone master branch
git clone https://github.com/utkarshkr100/mpp2.git
cd mpp2

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py

# Or run API
python start_api.py
```

### Live URLs:
- **Streamlit App**: https://your-app.streamlit.app
- **Local**: http://localhost:8501

### Features:
- 🎨 **Dynamic Form**: Fields adapt based on property type
- 📊 **Price Range**: Shows ±10% range instead of single price
- 🏆 **Location Premiums**: Auto-adjusts for luxury areas
- 📈 **Batch Predictions**: Upload CSV for multiple properties
- ✅ **Auto-fill**: Size suggests based on bedrooms
- ⚠️ **Validation**: Warns about unusual inputs

---

## 🚀 `api-only` Branch - FastAPI Backend

### What's Included:
- ✅ **api.py** - FastAPI REST API
- ✅ **start_api.py** - API launcher
- ✅ **All encoders** - Label encoders
- ✅ **Validation rules** - JSON files
- ✅ **Location multipliers** - Premium pricing
- ❌ **No UI files** - No Streamlit
- ❌ **No compressed model** - Must download separately

### Use Cases:
- ✅ Microservice architecture
- ✅ Mobile app backend
- ✅ Integration with other systems
- ✅ Production API deployment
- ✅ Bulk prediction service

### Deployment:
```bash
# Clone api-only branch
git clone -b api-only https://github.com/utkarshkr100/mpp2.git
cd mpp2

# Download model from Azure
curl -o model/random_forest_model.pkl YOUR_AZURE_URL

# Install dependencies
pip install -r requirements.txt

# Run API
python start_api.py
```

### Live URLs:
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/

### Endpoints:
```
GET  /                     - Health check
GET  /model-info           - Model information
GET  /options              - Available areas/types
POST /predict              - Single prediction
POST /predict-batch        - Batch predictions
```

### Model Storage:
The 181 MB model file must be stored separately:

1. **Upload to Azure Blob Storage**
2. **Generate SAS URL**
3. **Download during deployment**

See [MODEL_SETUP.md](MODEL_SETUP.md) for instructions.

---

## 🔄 Switching Between Branches

### Switch to master (UI):
```bash
git checkout master
pip install -r requirements.txt
streamlit run app.py
```

### Switch to api-only (Backend):
```bash
git checkout api-only
curl -o model/random_forest_model.pkl YOUR_AZURE_URL
pip install -r requirements.txt
python start_api.py
```

---

## 📁 File Structure Comparison

### `master` Branch:
```
mpp2/
├── app.py                    ✅ Streamlit UI
├── api.py                    ✅ FastAPI
├── start_streamlit.py        ✅ Launcher
├── start_api.py              ✅ Launcher
├── requirements.txt          ✅ Both UI + API deps
├── .streamlit/config.toml    ✅ UI config
├── model/
│   ├── random_forest_model.pkl.gz  ✅ 54 MB (compressed)
│   ├── label_encoder_*.pkl         ✅ Encoders
│   └── *.json                      ✅ Rules
└── README.md                 ✅ UI documentation
```

### `api-only` Branch:
```
mpp2/
├── api.py                    ✅ FastAPI only
├── start_api.py              ✅ Launcher
├── requirements.txt          ✅ API deps only
├── model/
│   ├── random_forest_model.pkl  ❌ NOT in Git (181 MB)
│   ├── label_encoder_*.pkl      ✅ Encoders
│   └── *.json                   ✅ Rules
├── README.md                 ✅ API documentation
└── MODEL_SETUP.md            ✅ Model download guide
```

---

## 🎯 Recommended Usage

### For Development & Testing:
→ Use **`master` branch** with Streamlit UI

### For Production API:
→ Use **`api-only` branch** with Azure deployment

### For Demo/Presentation:
→ Use **`master` branch** deployed on Streamlit Cloud

### For Mobile/Integration:
→ Use **`api-only` branch** as backend API

---

## 🚀 Deployment Scenarios

### Scenario 1: Streamlit Cloud (Free)
- Branch: `master`
- Platform: https://share.streamlit.io
- Files: All in Git (54 MB compressed model)
- Setup: Click deploy, select repo, done!

### Scenario 2: Azure Web App
- Branch: `api-only`
- Platform: Azure App Service
- Files: Download model from Azure Storage
- Setup: Deploy code + model download script

### Scenario 3: Docker Container
- Branch: `api-only`
- Platform: Any (AWS, GCP, Azure, etc.)
- Files: Build with model download
- Setup: Docker build with --build-arg MODEL_URL

### Scenario 4: Local Development
- Branch: Either
- Platform: Localhost
- Files: Clone and run locally
- Setup: pip install + run

---

## 📊 Model File Summary

### Compressed Model (master):
- **File**: `random_forest_model.pkl.gz`
- **Size**: 54 MB
- **Storage**: In Git Repository
- **Loading**: `gzip.open()` in Python
- **Performance**: Same (86.9% R²)

### Uncompressed Model (api-only):
- **File**: `random_forest_model.pkl`
- **Size**: 181 MB
- **Storage**: Azure Blob Storage
- **Loading**: `pickle.load()` in Python
- **Performance**: Same (86.9% R²)

Both use the identical Random Forest model (100 trees, depth 20).
The only difference is compression for Git storage.

---

## 🤝 Contributing

When making changes:

1. **UI Changes** → Work on `master` branch
2. **API Changes** → Work on `api-only` branch
3. **Model Updates** → Update both branches + Azure storage

---

## 📞 Support

- **Master Branch**: Streamlit UI with compressed model
- **API Branch**: FastAPI with external model storage
- **Issues**: https://github.com/utkarshkr100/mpp2/issues

---

## ✅ Current Status

- ✅ **master** - Deployed on Streamlit Cloud
- ✅ **api-only** - Ready for Azure deployment
- ✅ Model file uploaded to Azure Storage
- ✅ Documentation complete
