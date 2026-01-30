# GitHub Setup Guide for Citadel

**Phase 0, Week 1 - GitHub Repository Initialization**

---

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Create new repository:
   - **Name:** `citadel`
   - **Description:** "Autonomous capital fortress powered by TradeSynapse Protocol"
   - **Visibility:** Private (for now)
   - **Initialize:** Do NOT check "Initialize with README" (we already have one)

3. Copy the repository URL (HTTPS or SSH)

---

## Step 2: Initialize Local Git

Open terminal in `wallet-trial` folder:

```bash
# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: Citadel architecture blueprint & documentation"

# Add remote
git remote add origin https://github.com/[YOUR_USERNAME]/citadel.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 3: Set Up GitHub Secrets

For CI/CD pipelines to work, add these secrets:

1. Go to repo → Settings → Secrets and variables → Actions
2. Add these secrets:

```
FLY_API_TOKEN=               # From flyctl auth login
NEON_API_KEY=                # From neon.tech
UPSTASH_REDIS_TOKEN=         # From upstash.com
PINATA_API_KEY=              # From pinata.cloud
PINATA_API_SECRET=           # From pinata.cloud
WALLETCONNECT_PROJECT_ID=    # From walletconnect.com
```

---

## Step 4: Create GitHub Actions Workflows

Create `.github/workflows/` with these files:

### `tests.yml` - Run tests on every push

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: 3.12
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest tests/ -v --cov

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
      - run: cd frontend && npm install
      - run: cd frontend && npm run test

  contracts-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
      - run: cd contracts && npm install
      - run: cd contracts && npx hardhat test
```

---

## Step 5: Repository Settings

1. **Branch Protection:** Go to Settings → Branches
   - Protect `main` branch
   - Require pull request review (1 reviewer)
   - Require tests to pass before merging

2. **Collaborators:** Settings → Collaborators
   - Add team members with appropriate roles

3. **Labels:** Create labels for issues:
   - `backend` - Backend work
   - `frontend` - Frontend work
   - `contracts` - Smart contracts
   - `documentation` - Docs updates
   - `bug` - Bug reports
   - `feature` - Feature requests
   - `phase-1` - Phase 1 work
   - `phase-2` - Phase 2 work

---

## Step 6: Deployment Setup (Later)

This will be done in Week 2, but prepare now:

- **Fly.io:** `flyctl auth login` → Create apps for each service
- **Vercel:** Connect GitHub repo to Vercel for auto-deploy
- **Neon:** Create PostgreSQL database, get connection string
- **Upstash:** Create Redis cluster, get connection string

---

## Step 7: Local Development Workflow

```bash
# Create feature branch
git checkout -b feature/wallet-management

# Make changes, test locally
# ...

# Commit
git add .
git commit -m "feat: implement wallet management"

# Push
git push origin feature/wallet-management

# Create Pull Request on GitHub
# - GitHub Actions will run tests
# - Wait for review
# - Merge when approved
```

---

## Current Status: Week 1

- ✅ Local `.gitignore` created
- ✅ `.env.example` template created
- ✅ `README.md` created
- ✅ Directory structure created
- ⏳ GitHub repository (do this next)
- ⏳ GitHub Actions workflows
- ⏳ Secrets configured

---

**Next Action:** Create GitHub repo and push code

When ready, run:
```bash
cd wallet-trial
git remote add origin https://github.com/[YOUR_USERNAME]/citadel.git
git branch -M main
git push -u origin main
```

---

**Week 1 Completion:** Once this is done, move to Week 2 (Database Schema)
