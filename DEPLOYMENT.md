# 🚀 Streamlit Cloud Deployment Guide

Complete guide to deploy Dubai Real Estate Price Predictor on Streamlit Cloud using GitHub.

## 📋 Prerequisites

- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
- Git installed locally

## 🔧 Step-by-Step Deployment

### 1. Prepare Your Repository

The project is already configured for Streamlit Cloud deployment with:

- ✅ `.streamlit/config.toml` - Theme and server configuration
- ✅ `.gitignore` - Excludes large data files
- ✅ `requirements.txt` - All Python dependencies
- ✅ `README.md` - Project documentation
- ✅ Model files included (`.pkl` and `.json`)

### 2. Create GitHub Repository

```bash
# Navigate to your project folder
cd d:\Hayy\mpp2

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Dubai Real Estate Price Predictor"

# Create repository on GitHub and link it
git remote add origin https://github.com/YOUR_USERNAME/dubai-real-estate-predictor.git

# Push to GitHub
git push -u origin main
```

**Note**: Replace `YOUR_USERNAME` with your GitHub username.

### 3. Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create New App**
   - Click **"New app"** button
   - Select your repository: `YOUR_USERNAME/dubai-real-estate-predictor`
   - Set branch: `main`
   - Set main file path: `app.py`
   - Click **"Deploy!"**

3. **Wait for Deployment**
   - Streamlit will install dependencies from `requirements.txt`
   - Takes 2-5 minutes for initial deployment
   - You'll get a URL like: `https://your-app-name.streamlit.app`

### 4. Verify Deployment

Once deployed, check:
- ✅ App loads without errors
- ✅ Model files loaded correctly
- ✅ Predictions work
- ✅ Batch upload works
- ✅ All dropdowns populate

## 📦 What Gets Deployed

### Included in Git (deployed to cloud):
- ✅ `app.py` - Main application
- ✅ `api.py` - API backend (optional)
- ✅ `requirements.txt` - Dependencies
- ✅ `.streamlit/config.toml` - Configuration
- ✅ `model/*.pkl` - Trained models and encoders (~10 MB)
- ✅ `model/*.json` - Validation rules and multipliers

### Excluded from Git (not deployed):
- ❌ `data/*.csv` - Training data (too large)
- ❌ `test-data/*.csv` - Test data
- ❌ `figures/*.png` - Generated plots
- ❌ `__pycache__/` - Python cache

## ⚙️ Configuration Details

### requirements.txt
```
streamlit==1.31.0
pandas==2.2.0
numpy==1.26.3
scikit-learn==1.4.0
plotly==5.18.0
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
```

### .streamlit/config.toml
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true
```

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Make sure all imports in `app.py` are listed in `requirements.txt`

### Issue: "FileNotFoundError: model/*.pkl"
**Solution**: Ensure model files are not in `.gitignore` and are pushed to GitHub

### Issue: App is slow to load
**Solution**:
- Model files are cached with `@st.cache_resource`
- First load takes longer, subsequent loads are fast

### Issue: "Maximum upload size exceeded"
**Solution**: Already configured to 200MB in `config.toml`

## 🔄 Updating the App

After making changes:

```bash
# Make your changes to app.py or other files
git add .
git commit -m "Update: description of changes"
git push

# Streamlit Cloud auto-deploys on push to main branch
```

## 🎨 Customization

### Change App URL
- Go to Streamlit Cloud dashboard
- Click on your app → Settings → General
- Edit "App URL"

### Custom Domain (Pro feature)
- Upgrade to Streamlit Cloud Pro
- Add custom domain in settings

### Environment Variables (if needed)
- Settings → Secrets
- Add secrets in TOML format

## 📊 Resource Limits (Free Tier)

- **Memory**: 1 GB RAM
- **CPU**: Shared
- **Storage**: 1 GB
- **Concurrent users**: Unlimited (but shares resources)

Our app uses:
- ~100 MB for model files
- ~50 MB for runtime
- ~10 MB for dependencies
- **Total**: ~160 MB ✅ Well within limits

## 🔐 Security Best Practices

1. **No sensitive data**: Don't commit API keys or credentials
2. **Use Secrets**: For any configs, use Streamlit Secrets
3. **HTTPS**: Streamlit Cloud provides HTTPS by default
4. **XSRF Protection**: Already enabled in config

## 📈 Monitoring

- **View logs**: Click on app → "Manage app" → "Logs"
- **Analytics**: Settings → Analytics (shows usage stats)
- **Status**: Green dot = running, Red = error

## 🎯 Post-Deployment Checklist

After deployment, test:

- [ ] Homepage loads correctly
- [ ] All form fields populate
- [ ] Single prediction works
- [ ] Price range displays correctly
- [ ] Location multiplier applies
- [ ] Batch upload works
- [ ] CSV download works
- [ ] No console errors

## 📞 Support

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Community Forum**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **Status Page**: [streamlitstatus.com](https://streamlitstatus.com)

## 🎉 Success!

Your app is now live! Share the URL:
`https://your-app-name.streamlit.app`

---

**Pro Tips:**
- Star your repo to make it easier to find
- Add topics/tags to your GitHub repo: `streamlit`, `machine-learning`, `real-estate`, `dubai`
- Share on LinkedIn/Twitter to showcase your project
