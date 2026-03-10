# GitHub Setup & Publication Guide

Complete step-by-step instructions to publish your composite analysis repository on GitHub.

---

## PART 1: Create GitHub Repository

### Step 1.1: Create New Repository on GitHub.com

1. Go to [github.com](https://github.com) and log in
2. Click **"+"** button (top right) → **"New repository"**
3. Fill in:
   ```
   Repository name:     composipy-surrogate
   Description:         Multi-metric surrogate modeling for composite laminates
                        (Buckling Load Factor, Bending Deflection, Natural Frequency)

   Visibility:          Public
   Initialize:          ☐ Add .gitignore (we already have one)
                        ☐ Add LICENSE (we already have one)
                        ☐ Add README (we already have one)
   ```
4. Click **"Create repository"**

### Step 1.2: Get Your Repository URL
After creating, GitHub shows:
```
https://github.com/yourusername/composipy-surrogate.git
```
Copy this URL (you'll need it in Step 2).

---

## PART 2: Initialize Git & Commit Files Locally

### Step 2.1: Open Terminal in Project Folder

**Windows (PowerShell):**
```powershell
cd "C:\Users\Vijai Venkatesh\Desktop\740"
```

**Mac/Linux:**
```bash
cd ~/Desktop/740
```

### Step 2.2: Initialize Git

```bash
git init
```

This creates a hidden `.git` folder to track changes.

### Step 2.3: Verify Files Are Ready

```bash
git status
```

You should see all your files listed in red (untracked).

### Step 2.4: Add All Files

```bash
git add .
```

This stages all files for commit. Run `git status` again - files should turn green.

### Step 2.5: Create Initial Commit

```bash
git commit -m "Initial commit: Multi-metric composite laminate analysis

- Add notebook with 3 analysis modes (BLF, Bending, Frequency)
- Implement Morris Screening + Latin Hypercube Sampling
- Train polynomial Response Surface Model with Ridge regularization
- Include Sobol global sensitivity analysis
- Fix Boundary Condition mapping bug (SIMPLY_SUPPORTED)
- Comprehensive documentation (README, QUICKSTART, CONTRIBUTING)
- MIT License for open source use"
```

### Step 2.6: Verify Commit

```bash
git log
```

You should see your commit message.

---

## PART 3: Connect to GitHub & Push

### Step 3.1: Add Remote Repository

```bash
git remote add origin https://github.com/yourusername/composipy-surrogate.git
```

(Replace `yourusername` with your actual GitHub username)

### Step 3.2: Rename Main Branch (if needed)

Modern GitHub defaults to `main`, but older Git versions use `master`. Make sure they match:

```bash
git branch -M main
```

### Step 3.3: Push to GitHub

```bash
git push -u origin main
```

The `-u` flag sets `main` as the upstream branch (so future pushes are simpler).

### Step 3.4: Verify on GitHub

Go to your GitHub repository URL and refresh. You should see:
- All your files listed
- Commit history
- README displayed below file list

---

## PART 4: Add GitHub Features

### Step 4.1: Enable Discussions

1. Go to your repository
2. Click **Settings** (top right)
3. Scroll down to **Features** section
4. Check **☑ Discussions**
5. Save changes

This allows users to ask questions, share ideas without opening issues.

### Step 4.2: Set Repository Topics

1. Go to repository **home page**
2. Click **"Add topics"** (right sidebar, under repo name)
3. Add these topics (separate with spaces):
   ```
   composites
   surrogate-model
   response-surface-methodology
   python
   jupyter
   composipy
   composite-materials
   machine-learning
   ```
4. Click outside box to save

This helps people find your project.

### Step 4.3: Add Repository Description & Website (Optional)

1. Click repository **Settings**
2. In **General** section, find **Description**:
   ```
   Multi-metric surrogate modeling framework for composite laminated plates
   using ComposiPy, Morris Screening, LHS, and polynomial RSM
   ```
3. (Optional) Add **Website** if you have one
4. Click **Save changes**

---

## PART 5: Create a Release (Optional but Recommended)

### Step 5.1: Navigate to Releases

1. Go to your repository
2. Click **"Releases"** (right sidebar)
3. Click **"Create a new release"**

### Step 5.2: Fill in Release Details

```
Tag version:         v1.0.0
Release title:       Multi-Metric Surrogate Modeling Framework v1.0.0

Release notes:
## Overview
Initial release of the composite laminate analysis framework with support
for three analysis metrics:
- Buckling Load Factor (BLF)
- Bending Deflection
- Natural Frequency

## Key Features
✨ Single notebook with mode-switching architecture
✨ Asymmetric laminate support (8 independent fiber angles)
✨ Morris Screening for variable importance
✨ Latin Hypercube Sampling (3,500 design points)
✨ Polynomial Response Surface Model with Ridge regularization
✨ Comprehensive overfitting diagnostics
✨ Sobol global sensitivity analysis
✨ 12+ publication-quality visualizations

## What's Fixed
🐛 Boundary condition mapping bug (SIMPLY_SUPPORTED)
   - Old: ~16.5% simulation failures with Shear BC
   - New: <0.1% failure rate

## Documentation
📖 README.md (400+ lines) - Complete usage & physics details
📖 QUICKSTART.md - 5-minute setup & troubleshooting
📖 CONTRIBUTING.md - Development guidelines

## Requirements
- Python 3.8+
- ComposiPy 0.5+
- NumPy, SciPy, scikit-learn, matplotlib, seaborn, SALib

## Getting Started
See QUICKSTART.md for installation and first run (5 minutes)

## License
MIT - See LICENSE file
```

3. Click **"Publish release"**

---

## PART 6: Update GitHub Settings (Optional Advanced)

### Step 6.1: Branch Protection (Optional)

If you want to prevent accidental commits to main:

1. Go to **Settings → Branches**
2. Under "Branch protection rules" click **"Add rule"**
3. Enter `main` as branch name
4. Check options:
   - ☑ Require pull request reviews before merging
   - ☑ Require status checks to pass before merging
5. Save

### Step 6.2: Enable Auto-merge (Optional)

For convenient PR handling:

1. Go to **Settings → General**
2. Check **☑ Allow auto-merge**
3. Optionally auto-delete head branches after merge

### Step 6.3: Add Dependabot Alerts (Optional)

For automated security updates:

1. Go to **Settings → Code security and analysis**
2. Enable:
   - ☑ Dependabot alerts
   - ☑ Dependabot security updates
   - ☑ Secret scanning (if private repo)

---

## PART 7: Verification Checklist

### ✅ Pre-Publish Checklist

- [ ] GitHub repository created at `https://github.com/yourusername/composipy-surrogate`
- [ ] All files pushed to GitHub:
  ```bash
  git status
  # Should show "nothing to commit, working tree clean"
  ```
- [ ] README.md visible on repository homepage
- [ ] .gitignore excludes outputs and cache
- [ ] LICENSE file present and visible
- [ ] All 3 notebooks cells pass syntax check
- [ ] No sensitive data in repo (no API keys, credentials, local paths)
- [ ] Topics added (composites, surrogate-model, python, jupyter, composipy)
- [ ] Discussions enabled
- [ ] Release created with v1.0.0 tag
- [ ] QUICKSTART.md accessible (users see it immediately)

### ✅ On GitHub Repository Page

Check these are visible:
- [ ] README displayed below file browser
- [ ] Green "Code" button with HTTPS/SSH/GitHub CLI options
- [ ] "Releases" link showing v1.0.0
- [ ] "About" section (right sidebar) showing description + topics
- [ ] "Discussions" tab enabled

---

## PART 8: After Publishing - Common Tasks

### How to Add New Files Later

After initial publish, when you make changes:

```bash
# Make changes in your files
# Then commit and push:

git add .
git commit -m "Add feature or fix description"
git push origin main
```

### How to Create a New Release

When you update the notebook (e.g., add Mode D):

```bash
git tag v1.1.0
git push origin v1.1.0
```

Then go to GitHub Releases and edit the tag to add release notes.

### How to Fix a Typo in README

```bash
# Edit README.md locally
# Then:
git add README.md
git commit -m "Fix typo in README setup instructions"
git push origin main
```

### How to View Your Repository Statistics

On your repository page:
- **Insights** tab shows:
  - Code frequency (commits over time)
  - Network (branch history)
  - Contributors
  - Traffic
  - Community profile (checklist of best practices)

---

## PART 9: Share Your Repository

### Markdown Link (for papers, websites)
```markdown
[Composite Laminate Analysis - GitHub](https://github.com/yourusername/composipy-surrogate)
```

### Citation Format (for academic work)
```bibtex
@software{composipy_surrogate_2026,
  author = {Venkatesh, Vijai and Ganesh Babu, Natarajan},
  title = {Composite Laminate Analysis: Multi-Metric Surrogate Modeling},
  year = {2026},
  url = {https://github.com/yourusername/composipy-surrogate},
  note = {Python package using ComposiPy and SALib}
}
```

### Social Media Share
```
🎉 Just published: Multi-metric surrogate modeling for composite laminates!

3 analysis modes (Buckling, Bending, Frequency) in one notebook
✨ Morris Screening + Latin Hypercube Sampling
✨ Polynomial RSM with comprehensive diagnostics
✨ Sobol sensitivity analysis

Open source (MIT) → https://github.com/yourusername/composipy-surrogate
```

---

## PART 10: Troubleshooting

### Problem: "fatal: not a git repository"
**Solution:** Make sure you're in the correct folder:
```bash
cd "C:\Users\Vijai Venkatesh\Desktop\740"
git status  # Should work now
```

### Problem: "error: The current branch main has no upstream branch"
**Solution:** Use `-u` flag when pushing:
```bash
git push -u origin main
```

### Problem: "Authentication failed" when pushing
**Solution:** You need to authenticate with GitHub. Use one of:

**Option A: Personal Access Token (Recommended)**
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token"
3. Check: ☑ repo (full control of private repos)
4. Copy the token
5. When Git asks for password, paste the token instead

**Option B: SSH Key (Advanced)**
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
# Add public key to GitHub → Settings → SSH Keys
git remote set-url origin git@github.com:yourusername/composipy-surrogate.git
```

### Problem: "nothing to commit" but files show in status
**Solution:** Files might be in .gitignore. Check:
```bash
cat .gitignore
```
If important files are excluded, edit .gitignore to remove them.

### Problem: "file too large" error
**Solution:** Git has a 100MB limit. For notebook:
1. Clear cell outputs before pushing:
   ```bash
   jupyter nbconvert --to notebook --ClearOutputPreprocessor.enabled=True Buckling_Load_Factor_Analysis.ipynb --inplace
   ```
2. Commit and push again

---

## PART 11: Quick Command Reference

### Most Common Commands After Initial Setup

```bash
# Check status of changes
git status

# Add all changes
git add .

# Commit with message
git commit -m "Your message here"

# Push to GitHub
git push

# Pull latest from GitHub (if working with others)
git pull

# View commit history
git log --oneline

# Undo last commit (but keep files)
git reset --soft HEAD~1

# View what changed
git diff

# Create new branch (for features)
git checkout -b feature/your-feature-name

# Switch to main
git checkout main

# Delete local branch
git branch -d feature/your-feature-name
```

---

## PART 12: Final Summary

### What You Should Have on GitHub

```
✅ Repository: github.com/yourusername/composipy-surrogate
   ├── Buckling_Load_Factor_Analysis.ipynb (main notebook)
   ├── create_pptx.js (PowerPoint generator)
   ├── README.md (400+ line documentation)
   ├── QUICKSTART.md (5-minute setup guide)
   ├── CONTRIBUTING.md (developer guidelines)
   ├── GITHUB_SETUP.md (this file)
   ├── LICENSE (MIT)
   ├── .gitignore (excludes outputs)
   ├── package.json (for PPT generation)
   └── package-lock.json

✅ Releases: v1.0.0 published with release notes

✅ Topics: composites, surrogate-model, python, jupyter, composipy

✅ Discussions: Enabled for community

✅ Visibility: Public (anyone can fork/star)
```

### Time to Complete Everything

| Step | Time |
|------|------|
| 1. Create GitHub repo | 2 min |
| 2. Initialize Git & commit | 3 min |
| 3. Push to GitHub | 2 min |
| 4. Add features (topics, discussions) | 3 min |
| 5. Create release | 5 min |
| **Total** | **~15 min** |

---

## Ready to Go? 🚀

You now have everything needed to publish professional-grade code on GitHub.

**Next steps:**
1. Run through PART 1-3 (basic setup)
2. Then add features from PART 4-5
3. Use PART 11 for ongoing maintenance

Good luck! 🎉

---

**Questions?** Check GitHub's official docs: https://docs.github.com
