# 📦 Model File Setup for API Branch

The `random_forest_model.pkl` file (181 MB) is too large for GitHub and must be stored separately.

## 📥 Download Model File

The model file needs to be placed in the `model/` directory before running the API.

### Option 1: Azure Storage Account (Recommended)

```bash
# Download from Azure Blob Storage
az storage blob download \
  --account-name YOUR_STORAGE_ACCOUNT \
  --container-name models \
  --name random_forest_model.pkl \
  --file model/random_forest_model.pkl
```

### Option 2: Direct Download

If model is hosted elsewhere:

```bash
# Download from URL
curl -o model/random_forest_model.pkl https://your-storage-url.com/random_forest_model.pkl

# Or using wget
wget -O model/random_forest_model.pkl https://your-storage-url.com/random_forest_model.pkl
```

### Option 3: Copy from Local

If you have the model file locally:

```bash
# Copy from another location
cp /path/to/random_forest_model.pkl model/
```

## ✅ Verify Model File

After downloading, verify the file:

```bash
# Check file exists and size
ls -lh model/random_forest_model.pkl

# Should show approximately 181 MB
# -rw-r--r-- 1 user group 181M date random_forest_model.pkl
```

## 🚀 Start the API

Once the model file is in place:

```python
# Test model loading
python -c "import pickle; model = pickle.load(open('model/random_forest_model.pkl', 'rb')); print('✓ Model loaded successfully!')"

# Start API
python start_api.py
```

## 📊 Model Details

- **File**: `random_forest_model.pkl`
- **Size**: 181 MB
- **Algorithm**: Random Forest Regressor
- **Estimators**: 100 trees
- **Max Depth**: 20
- **Performance**: 86.9% R², 16.69% MAPE

## 🔐 Azure Storage Setup (For Deployment)

### Upload to Azure

```bash
# Create storage account and container
az storage account create --name dubairealestate --resource-group rg-dubai-api
az storage container create --name models --account-name dubairealestate

# Upload model
az storage blob upload \
  --account-name dubairealestate \
  --container-name models \
  --name random_forest_model.pkl \
  --file model/random_forest_model.pkl
```

### Get Download URL

```bash
# Generate SAS token (valid for 1 year)
az storage blob generate-sas \
  --account-name dubairealestate \
  --container-name models \
  --name random_forest_model.pkl \
  --permissions r \
  --expiry 2026-12-31 \
  --https-only \
  --output tsv
```

## 🐳 Docker Setup

If using Docker, download model during build:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download model from Azure
ARG MODEL_URL
RUN curl -o model/random_forest_model.pkl "${MODEL_URL}"

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build with:

```bash
docker build --build-arg MODEL_URL="https://..." -t dubai-api .
```

## ⚠️ Important

- **Never commit** the 181 MB model file to Git
- **Always use** external storage (Azure, S3, GCS, etc.)
- **Keep model file** in `.gitignore`
- **Document** the download URL in deployment docs

## 📁 Required Files in Git

These files ARE committed to Git:

- ✅ `api.py` - FastAPI application
- ✅ `model/label_encoder_area.pkl` (3 KB)
- ✅ `model/label_encoder_subtype.pkl` (319 bytes)
- ✅ `model/label_encoder_regtype.pkl` (286 bytes)
- ✅ `model/metadata.pkl` (5 KB)
- ✅ `model/*.json` - Validation rules (500 KB total)
- ❌ `model/random_forest_model.pkl` (181 MB) - **NOT in Git**

## 🎯 Quick Start

```bash
# 1. Clone repository
git clone -b api-only https://github.com/utkarshkr100/mpp2.git
cd mpp2

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download model (replace with your URL)
curl -o model/random_forest_model.pkl YOUR_MODEL_URL

# 4. Start API
python start_api.py

# 5. Test
curl http://localhost:8000/
```

## 📞 Support

If you need the model file, contact the repository maintainer for the Azure storage URL or download link.
