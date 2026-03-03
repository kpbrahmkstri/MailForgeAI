# 🚀 MailForgeAI Hugging Face Spaces Deployment Guide

## Overview

MailForgeAI is now fully configured for deployment on Hugging Face Spaces with proper path handling using `pathlib.Path`. This ensures the application works seamlessly in containerized environments and cloud deployments.

## ✅ Changes Made for HF Deployment

### 1. **Pathlib Integration**
All static file paths have been converted to use `pathlib.Path`:

- **Created**: `src/utils/path_utils.py` - Centralized path management
- **Updated Files**:
  - `src/memory/memory_store.py`
  - `src/agents/personalization_agent.py`
  - `src/rag/template_rag.py`
  - `generate_workflow_diagram.py`
  - `generate_png_diagram.py`
  - `convert_svg_to_png.py`
  - `generate_png_pillow.py`

### 2. **Environment Variables Support**
The path utility respects the `PROJECT_ROOT` environment variable for containerized deployments:
```python
if "PROJECT_ROOT" in os.environ:
    return Path(os.environ["PROJECT_ROOT"])
```

### 3. **Automatic Directory Creation**
All directory access includes automatic creation with `mkdir(parents=True, exist_ok=True)`, so no pre-existing directories are required.

### 4. **Streamlit App Ready**
The app is configured in `app.py` for HF Spaces deployment with:
- Proper imports using pathlib
- Environment variable support
- Secrets management integration
- Clean UI/UX

---

## 📋 Prerequisites

1. **Hugging Face Account** - Sign up at https://huggingface.co
2. **OpenAI API Key** - Get from https://platform.openai.com/api-keys
3. **Git** (optional) - For cloning/pushing repositories

---

## 🎯 Step-by-Step Deployment

### **Method 1: Using Hugging Face Web Interface (Easiest)**

#### Step 1: Create a New Space
1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in the form:
   - **Space name**: `mailforgeai` (or your preferred name)
   - **License**: Select `OpenRAIL-M` or `Apache 2.0`
   - **Select the Space SDK**: Choose **Streamlit**
   - **Space Hardware**: Select **CPU** (or **GPU** if needed)
4. Click **"Create Space"**

#### Step 2: Add Files to Space
Online editor method:
1. Open your created Space
2. Click **"Files"** tab
3. Use the web editor to upload/create files:
   - Create the directory structure matching your project
   - Upload `app.py` and all source files
   - Upload `requirements.txt`

**OR** Use Git method:
```bash
# Clone your HF Space
git clone https://huggingface.co/spaces/<your-username>/<space-name>
cd <space-name>

# Copy your project files
cp -r /path/to/MailForgeAI/* .

# Push to HF
git add .
git commit -m "Initial MailForgeAI deployment"
git push
```

#### Step 3: Add Secret Variables
1. Go to your Space settings (⚙️ icon)
2. Scroll to **"Repository secrets"**
3. Click **"New secret"**
4. Add secret:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: (paste your OpenAI API key)
5. Click **"Save"**

#### Step 4: Deploy
The space should automatically build and deploy!
- Check the **"Build"** logs for any issues
- Once green, your app is live at: `https://huggingface.co/spaces/<username>/<space-name>`

---

### **Method 2: Using Git (For Version Control)**

#### Step 1-2: Create Space (same as above)

#### Step 3: Configure Git with HF Token
```bash
# Create HF token at https://huggingface.co/settings/tokens
huggingface-cli login
# Enter your HF token when prompted
```

#### Step 4: Clone and Push
```bash
# Clone your HF Space
git clone https://huggingface.co/spaces/<your-username>/<space-name>
cd <space-name>

# Add your project files (maintaining structure)
git add .
git commit -m "Initial MailForgeAI deployment"
git push
```

#### Step 5: Add Secrets via API or CLI
```bash
huggingface-cli add-secret OPENAI_API_KEY "your-api-key-here" --repo-id "<username>/<space-name>"
```

---

## 🔧 Configuration Files

### File Structure Required
```
your-hf-space/
├── app.py                           # Main Streamlit app
├── requirements.txt                 # Python dependencies
├── src/
│   ├── __init__.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── path_utils.py            # Path management (CRITICAL)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── input_parser_agent.py
│   │   ├── intent_detection_agent.py
│   │   ├── tone_stylist_agent.py
│   │   ├── personalization_agent.py
│   │   ├── draft_writer_agent.py
│   │   ├── review_agent.py
│   │   ├── router_agent.py
│   │   └── retrieval_agent.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   └── openai_client.py
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── memory_store.py
│   │   └── user_profiles.json
│   ├── rag/
│   │   ├── __init__.py
│   │   └── template_rag.py
│   ├── workflow/
│   │   ├── __init__.py
│   │   └── langgraph_flow.py
│   └── ui/
│       └── __init__.py
├── data/
│   ├── kb/
│   │   └── templates/               # Email templates (.md files)
│   └── tone_samples/
└── .gitignore
```

---

## 🔐 Environment Variables

Set these in your HF Space **"Repository secrets"**:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key |
| `OPENAI_MODEL` | ❌ No | Model name (default: `gpt-4o-mini`) |
| `PROJECT_ROOT` | ❌ No | Override project root path |

---

## 📝 Streamlit Secrets Alternative

If you prefer using Streamlit secrets files instead of HF Repository secrets:

1. Navigate to **Settings** → **Secrets**
2. Add your secrets in TOML format:
```toml
[general]
openai_api_key = "sk-..."
openai_model = "gpt-4o-mini"
```

Access in code:
```python
import streamlit as st
api_key = st.secrets["general"]["openai_api_key"]
```

---

## 🧪 Testing Locally Before Deployment

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
export OPENAI_API_KEY="your-key-here"

# 3. Run the app locally
streamlit run app.py

# 4. Open browser to http://localhost:8501
```

---

## 💡 Path Handling Details

### How pathlib.Path Helps in HF Spaces

**Before (Static Paths):**
```python
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "kb", "templates")
```
❌ Breaks when directory structure changes or in containerized environments

**After (Using pathlib):**
```python
from src.utils.path_utils import get_templates_dir
TEMPLATE_DIR = get_templates_dir()  # Automatically creates if missing!
```
✅ Works in any environment - containerized, cloud, local

### Key Features
- ✅ Cross-platform compatibility (Windows, Linux, macOS)
- ✅ Automatic directory creation
- ✅ Environment variable override support
- ✅ Type-safe Path objects
- ✅ Cleaner, more readable code

---

## 🚨 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"
**Solution:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### Issue: "FileNotFoundError" for data files
**Solution:**
Make sure files are in your HF Space repository:
```bash
# Check file exists
ls data/kb/templates/
```

### Issue: OpenAI API errors
**Solution:**
1. Verify `OPENAI_API_KEY` is set in HF Secrets
2. Check API key has sufficient credits at https://platform.openai.com/account/billing/overview
3. Ensure key is not revoked

### Issue: Chroma database errors
**Solution:**
- Chroma database is created automatically on first run
- Uses `data/chroma_templates/` directory
- May take 1-2 minutes on first run for embeddings

---

## 📊 Monitoring & Logs

**View Logs in HF Spaces:**
1. Open your Space
2. Click **"Logs"** (in the top right)
3. Follow real-time execution logs

**Common Log Messages:**
- ✅ `✅ Mermaid diagram saved to: ...` - Setup successful
- 🔄 `🔄 Generating your email...` - Processing request
- ✅ `Email generated successfully!` - Success message

---

## 🔄 Updating Your Deployment

**Via Git:**
```bash
cd your-space-directory
git add .
git commit -m "Update: <description>"
git push
```

**Via Web Editor:**
1. Open your Space
2. Click **"Files"**
3. Edit and save files
4. Space automatically redeploys

---

## 📞 Support & Resources

- **HF Spaces Docs**: https://huggingface.co/docs/hub/spaces
- **Streamlit Docs**: https://docs.streamlit.io
- **OpenAI API Docs**: https://platform.openai.com/docs
- **LangGraph Docs**: https://github.com/langchain-ai/langgraph
- **GitHub Discussions**: https://github.com/huggingface/hub-docs/discussions

---

## ✨ Next Steps

1. ☑️ Deploy your first version
2. ☑️ Test with sample emails
3. ☑️ Adjust prompts and templates as needed
4. ☑️ Share your Space with the community!
5. ☑️ Collect feedback and iterate

---

**Happy Deploying! 🚀**
