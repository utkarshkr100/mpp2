# 🚨 Large Model File Issue & Solutions

## Problem

The Random Forest model file is **181 MB**, which exceeds:
- GitHub's 100 MB file size limit
- Streamlit Cloud's optimal performance recommendations

## ✅ Solution Options

### Option 1: Use Git LFS (Recommended for GitHub)

Git Large File Storage (LFS) allows you to store large files on GitHub.

```bash
# Install Git LFS
git lfs install

# Track the large model file
git lfs track "model/random_forest_model.pkl"

# Add the .gitattributes file
git add .gitattributes

# Commit and push
git add model/random_forest_model.pkl
git commit -m "Add model using Git LFS"
git push origin main
```

**Pros:**
- Keep existing high-performance model
- Works with GitHub
- Streamlit Cloud supports Git LFS

**Cons:**
- Requires Git LFS setup
- Slower deployments
- Free GitHub LFS has 1 GB storage limit

---

### Option 2: Retrain with Smaller Model (Recommended for Streamlit)

Create a lighter model with fewer trees while maintaining good performance.

**Create new training script: `train_lightweight_model.py`**

```python
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# Load data
df = pd.read_csv('data/transaction_2025_cleaned.csv')

# Prepare features (same as before)
# ... [feature engineering code] ...

# Train SMALLER Random Forest
model = RandomForestRegressor(
    n_estimators=30,        # Reduced from 100
    max_depth=15,           # Reduced from 20
    min_samples_split=10,   # Increased from 2
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Save model
with open('model/random_forest_model.pkl', 'wb') as f:
    pickle.dump(model, f, protocol=4)  # Use protocol 4 for compression

print(f"Model size: {os.path.getsize('model/random_forest_model.pkl') / 1024 / 1024:.1f} MB")
print(f"R² Score: {model.score(X_test, y_test):.4f}")
```

**Expected Results:**
- Model size: ~20-30 MB (6x smaller)
- R² Score: ~0.83-0.85 (slight decrease from 0.87)
- Still good performance for predictions

**Pros:**
- No Git LFS needed
- Faster deployments
- Works directly with GitHub
- Faster predictions

**Cons:**
- Slightly lower accuracy (2-3% decrease)
- Need to retrain model

---

### Option 3: Use Gradient Boosting Instead

Switch to a more compact model architecture.

```python
from sklearn.ensemble import GradientBoostingRegressor

# Train Gradient Boosting (naturally more compact)
model = GradientBoostingRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)

model.fit(X_train, y_train)
```

**Expected Results:**
- Model size: ~5-10 MB
- R² Score: ~0.84-0.86
- Comparable performance

**Pros:**
- Very small file size
- Often better performance per tree
- No Git LFS needed

**Cons:**
- Slower training
- Slower predictions than Random Forest

---

### Option 4: Upload Model Separately (Not Recommended)

Store model outside GitHub and download on startup.

```python
# In app.py
import urllib.request
import os

@st.cache_resource
def download_model():
    if not os.path.exists('model/random_forest_model.pkl'):
        url = "https://your-cloud-storage.com/model.pkl"
        urllib.request.urlretrieve(url, 'model/random_forest_model.pkl')

    with open('model/random_forest_model.pkl', 'rb') as f:
        return pickle.load(f)
```

**Pros:**
- Keep large model
- No Git LFS needed

**Cons:**
- Need external hosting (Dropbox, Google Drive, AWS S3)
- Slow first load
- Reliability issues
- Complex setup

---

## 🎯 Recommended Approach

**For quick deployment: Option 2 - Retrain Smaller Model**

1. Retrain with fewer estimators (30-50 instead of 100)
2. Model will be ~20-30 MB (under 100 MB limit)
3. Still 83-85% R² (very good performance)
4. Deploy directly to GitHub and Streamlit Cloud

**Script to create smaller model:**

```bash
# Create the training script
python train_lightweight_model.py

# Check size
ls -lh model/random_forest_model.pkl

# Should be under 50 MB
```

---

## 📊 Model Size Comparison

| Model Type | Estimators | Size | R² Score | Deploy Method |
|------------|-----------|------|----------|---------------|
| Current RF | 100 trees | 181 MB | 0.869 | Git LFS |
| Light RF | 30 trees | ~25 MB | ~0.84 | Direct Git |
| Light RF | 50 trees | ~40 MB | ~0.85 | Direct Git |
| Gradient Boost | 100 trees | ~8 MB | ~0.85 | Direct Git |

---

## 🚀 Quick Fix Command

If you want to proceed with Git LFS:

```bash
# Install Git LFS (one time)
git lfs install

# Track model file
git lfs track "model/random_forest_model.pkl"

# Update .gitignore to remove model exclusion
# (Comment out the line: model/random_forest_model.pkl)

# Commit
git add .gitattributes model/random_forest_model.pkl
git commit -m "Add model with Git LFS"
git push origin main
```

---

## ⚠️ Current Status

The `.gitignore` currently excludes `model/random_forest_model.pkl` to prevent push errors.

**You need to choose one of the solutions above before deploying to Streamlit Cloud.**

---

## 📝 Next Steps

1. **Choose a solution** (Option 1 or 2 recommended)
2. **Implement the solution**
3. **Test locally**: `streamlit run app.py`
4. **Commit and push to GitHub**
5. **Deploy to Streamlit Cloud**

---

**Recommendation**: Use **Option 2** (retrain smaller model) for fastest deployment with minimal setup.
