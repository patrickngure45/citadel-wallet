# Phase 0, Week 1: Infrastructure Setup Checklist

**Citadel: Your Capital Fortress**  
**Brand:** Citadel | **Protocol:** TradeSynapse  
**Week:** 1 of 2 (Phase 0)

---

## ✅ COMPLETED (This Session)

- [x] Documentation created (8 documents)
- [x] Brand/protocol naming finalized (Citadel × TradeSynapse)
- [x] `.gitignore` created
- [x] `.env.example` created
- [x] `README.md` created
- [x] Directory structure created
- [x] GitHub setup guide created

---

## 🔄 IN PROGRESS (This Week)

### Infrastructure Accounts

**GitHub Repository**
- [ ] Create private repo: `citadel`
- [ ] Initialize local git & push
- [ ] Set up branch protection on `main`
- [ ] Create GitHub labels
- See: `GITHUB_SETUP.md`

**Fly.io (Backend Hosting)**
- [ ] Create account at https://fly.io
- [ ] Create 6 apps:
  - `citadel-perception` (Perception service)
  - `citadel-memory` (Memory service)
  - `citadel-risk` (Risk service)
  - `citadel-strategy` (Strategy service)
  - `citadel-execution` (Execution service)
  - `citadel-signing` (Signing service - isolated)
- [ ] Add `fly.toml` to repo
- [ ] Store `FLY_API_TOKEN` in GitHub Secrets

**Neon PostgreSQL (Database)**
- [ ] Create account at https://console.neon.tech
- [ ] Create project: `citadel-prod`
- [ ] Create branch: `development`
- [ ] Get connection string
- [ ] Store in `.env.local` as `DATABASE_URL`
- [ ] Note: Don't commit actual string to git

**Upstash Redis (Cache)**
- [ ] Create account at https://console.upstash.com
- [ ] Create Redis cluster
- [ ] Get connection string
- [ ] Store in `.env.local` as `REDIS_URL`

**Pinata IPFS (Audit Trail Storage)**
- [ ] Create account at https://pinata.cloud
- [ ] Create API key
- [ ] Get API key + secret
- [ ] Store in `.env.local`

**Vercel (Frontend Hosting)**
- [ ] Create account at https://vercel.com
- [ ] Connect GitHub repository
- [ ] Configure env vars
- [ ] Enable auto-deploy

**WalletConnect (MetaMask Integration)**
- [ ] Create account at https://cloud.walletconnect.com
- [ ] Create new project
- [ ] Get Project ID
- [ ] Store in `.env.local`

---

## 📋 WEEK 1 COMPLETION CRITERIA

All items below must be ✅ to mark Week 1 complete:

### Code Repository
- [ ] GitHub repo created and code pushed
- [ ] `.gitignore` preventing secrets
- [ ] `.env.example` template exists
- [ ] `README.md` complete with setup instructions
- [ ] Directory structure matches plan

### Infrastructure
- [ ] Fly.io account + 6 apps created
- [ ] Neon PostgreSQL account + database
- [ ] Upstash Redis account + cluster
- [ ] Pinata IPFS account + API keys
- [ ] Vercel account + repo connected
- [ ] WalletConnect project created

### Configuration
- [ ] `.env.local` (local development) created
- [ ] GitHub Secrets configured
- [ ] All connection strings obtained
- [ ] No secrets committed to git

### Documentation
- [ ] This checklist filled out
- [ ] README has setup instructions
- [ ] GITHUB_SETUP.md guide completed
- [ ] All docs reference Citadel brand

---

## 🔧 LOCAL SETUP (If Not Already Done)

```bash
# Initialize git
cd wallet-trial
git init
git add .
git commit -m "Initial commit: Citadel Phase 0"

# Create .env.local from template
cp .env.example .env.local
# Edit .env.local with your actual keys
```

---

## 📱 VERCEL SETUP (After GitHub)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Connect project
cd frontend
vercel link

# Deploy
vercel --prod
```

---

## 🚀 AFTER WEEK 1: MOVE TO WEEK 2

Once all Week 1 items are ✅:

1. Create `DATABASE_SCHEMA.md` (PostgreSQL tables)
2. Create `API_CONTRACTS.md` (FastAPI endpoints)
3. Create `SMART_CONTRACTS.md` (Solidity code)
4. Create `FRONTEND_ROUTES.md` (Next.js pages)
5. Create `ENTITY_COMMUNICATION.md` (Ably channels)

---

## 📞 NEED HELP?

- GitHub setup? → Read `GITHUB_SETUP.md`
- Confused about infrastructure? → Check docs
- Questions? → Ask before moving to Week 2

---

## 🎯 WEEK 1 GOAL

**By end of Week 1, you should have:**
- ✅ Git repo ready for code
- ✅ All infrastructure accounts created
- ✅ Local development environment configured
- ✅ Team can push code to GitHub
- ✅ CI/CD ready to test code
- ✅ Ready to start Week 2 technical specs

---

**Status:** In Progress  
**Week:** 1 of 2  
**Phase:** 0 (Infrastructure)  
**Next:** Move to Week 2 when all ✅ complete
