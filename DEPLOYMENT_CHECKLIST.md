# 🚀 MailForgeAI HF Spaces Deployment Checklist

## Pre-Deployment (Local)

- [ ] All static paths converted to `pathlib.Path`
- [ ] `src/utils/path_utils.py` created and working
- [ ] `app.py` configured for Streamlit
- [ ] `requirements.txt` updated with all dependencies
- [ ] Test locally: `streamlit run app.py`
- [ ] `.gitignore` configured with HF-specific entries

## HF Spaces Setup

- [ ] Create HF account at https://huggingface.co
- [ ] Create new Space: https://huggingface.co/spaces
  - [ ] Name: `mailforgeai`
  - [ ] SDK: Streamlit
  - [ ] License: Apache 2.0 or OpenRAIL-M

## Files Upload

### Method A: Web Editor
- [ ] Navigate to Files tab
- [ ] Create folder structure
- [ ] Upload all files matching the project structure

### Method B: Git (Recommended)
- [ ] Install `huggingface-hub`: `pip install huggingface-hub`
- [ ] Login: `huggingface-cli login`
- [ ] Clone Space: `git clone https://huggingface.co/spaces/<user>/<space-name>`
- [ ] Copy project files
- [ ] Push: `git add . && git commit -m "Initial deploy" && git push`

## Secrets Configuration

- [ ] Go to Space Settings (⚙️)
- [ ] Find "Repository secrets"
- [ ] Add secret:
  - Name: `OPENAI_API_KEY`
  - Value: (your OpenAI API key from https://platform.openai.com/api-keys)

## Verification

- [ ] Check Build logs (click "Logs")
- [ ] Wait for "Successfully built" message
- [ ] Test the app in browser
- [ ] Try generating sample email

## Monitoring

- [ ] Check logs periodically
- [ ] Monitor API usage at OpenAI dashboard
- [ ] Update code when needed via git push

---

## 📂 Critical Files for Deployment

**Must include:**
- ✅ `app.py` - Main Streamlit app
- ✅ `requirements.txt` - Dependencies
- ✅ `src/utils/path_utils.py` - Path management (NEW & CRITICAL)
- ✅ `src/workflow/langgraph_flow.py` - Core workflow
- ✅ All agent files in `src/agents/`
- ✅ All files in `src/integrations/`, `src/memory/`, `src/rag/`
- ✅ `data/kb/templates/` - Email templates (empty OK, will be created)

**Nice to have:**
- 📄 `README.md` - Project description
- 📄 `README_HF_DEPLOYMENT.md` - Deployment guide
- `.gitignore` - Git configuration

---

## 🔍 Files Changed for Pathlib Support

```
✅ MODIFIED:
- src/memory/memory_store.py
- src/agents/personalization_agent.py
- src/rag/template_rag.py
- generate_workflow_diagram.py
- generate_png_diagram.py
- convert_svg_to_png.py
- generate_png_pillow.py

✅ CREATED:
- src/utils/path_utils.py (CRITICAL - enables cloud deployment)
- app.py (optimized for HF Spaces)
- README_HF_DEPLOYMENT.md (this guide)

✅ UPDATED:
- requirements.txt
- .gitignore
```

---

## 📊 Quick Command Reference

### Local Testing
```bash
# Install deps
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="sk-..."

# Run app
streamlit run app.py

# Navigate to http://localhost:8501
```

### HF Deployment
```bash
# Install HF tools
pip install huggingface-hub

# Login to HF
huggingface-cli login

# Clone your space
git clone https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME
cd YOUR-SPACE-NAME

# Copy project
cp -r /path/to/MailForgeAI/* .

# Push to HF
git add .
git commit -m "Deploy MailForgeAI"
git push

# Add secrets (optional alternative to web interface)
huggingface-cli add-secret OPENAI_API_KEY "your-key" --repo-id YOUR-USERNAME/YOUR-SPACE-NAME
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Don't:**
- Commit `OPENAI_API_KEY` to repository (use Secrets!)
- Use hardcoded paths like `/home/user/...`
- Skip the `src/utils/path_utils.py` module
- Forget to upload `data/kb/templates/` folder
- Upload `.env` files (use Secrets instead)

✅ **Do:**
- Use `pathlib.Path` for all file operations
- Use environment variables for all secrets
- Test locally before pushing
- Keep dependencies updated
- Monitor logs after deployment

---

## 🎯 Expected Behavior After Deployment

✅ Space builds successfully (green ✓)
✅ App loads in browser
✅ Can enter email prompt
✅ Can select tone and recipient info
✅ Click "Generate Email" works
✅ Email is generated and displayed
✅ Can download as text file
✅ View agent trace and history

---

## 📈 Next Steps After Deployment

1. 🧪 Test with various email types
2. 📝 Add more email templates to `data/kb/templates/`
3. 👤 Customize user profiles in `data/memory/user_profiles.json`
4. 🎨 Adjust tone samples in `data/tone_samples/`
5. 🚀 Share Space URL with users
6. 📊 Monitor usage and feedback

---

Last Updated: 2026-03-02
MailForgeAI v1.0 - Ready for Hugging Face Spaces! 🚀
