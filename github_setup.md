# GitHub Setup Guide

Follow these steps to push the `merged` project to your GitHub repository.

---

## 1. Create a New Repository on GitHub
1. Go to [github.com](https://github.com) and log in.
2. Click the **+** icon in the top-right corner and select **New repository**.
3. Name it (e.g., `Phishing-Detection-Ensemble`) and click **Create repository**.
4. **Do not** initialize with a README, license, or .gitignore (we already have them).

---

## 2. Initialize and Push from Your Terminal
Open a terminal (PowerShell or Command Prompt) in `D:\FINAL YEAR PROJECT\merged` and run:

```powershell
# 1. Initialize Git repository
git init

# 2. Add all files (the .gitignore will automatically skip the venv and .env)
git add .

# 3. Create initial commit
git commit -m "Initial commit of merged phishing detection project"

# 4. Set main branch name
git branch -M main

# 5. Connect to your GitHub repository
# REPLACE <your-repo-url> with the URL from your GitHub repo (e.g., https://github.com/username/repo.git)
git remote add origin <your-repo-url>

# 6. Push to GitHub
git push -u origin main
```

---

## Important Notes:
- **Environment Variables:** The `.env` file contains configuration and is **ignored** by Git for security. You will need to manually recreate it or share it securely if others work on the project.
- **Large Files & Git LFS:** The new `phishing_deep_clean_v1.pkl` contains a **VotingClassifier Ensemble** combining 5 different models (Logistic Regression, LinearSVC, RandomForest, HistGradientBoosting, XGBoost). This makes the `.pkl` file substantially larger than previous single-model iterations. If the file exceeds GitHub's 100MB strict limit, you **must** use [Git LFS](https://git-lfs.github.com) to successfully track and push the `models/` directory.
