# MergeMind Deployment Guide

This guide covers deploying MergeMind to Render.com (backend) and Vercel (frontend).

---

## Part 1: Deploy Backend to Render.com

### Step 1: Sign Up
1. Go to [render.com](https://render.com)
2. Click **"Get Started"** → Sign in with GitHub

### Step 2: Create Web Service
1. Click **"New +"** → Select **"Web Service"**
2. Select **"Build and deploy from a Git repository"**
3. Find and select your **MergeMind** repo → Click **"Connect"**

### Step 3: Configure Settings
Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `mergemind` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

### Step 4: Add Environment Variables
Scroll to **"Environment Variables"** and add:

```
GROQ_API_KEY        =  gsk_your_groq_key_here
GITHUB_TOKEN        =  ghp_your_github_token_here
ALLOWED_ORIGINS     =  http://localhost:3000
```

### Step 5: Deploy
1. Click **"Create Web Service"** at the bottom
2. Wait 3-5 minutes for first deployment

### Step 6: Test Backend
Once deployed, you'll get a URL like: `https://mergemind.onrender.com`

Test it:
```
https://mergemind.onrender.com/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "...", "version": "1.0.0", ...}
```

**Copy this URL** - you'll need it for the frontend!

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Sign Up
1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub

### Step 2: Import Project
1. Click **"Add New..."** → **"Project"**
2. Find and import your **MergeMind** repo

### Step 3: Configure
| Field | Value |
|-------|-------|
| **Framework Preset** | `Next.js` |
| **Root Directory** | `frontend` |

### Step 4: Add Environment Variables
Expand **"Environment Variables"** and add:

```
NEXT_PUBLIC_API_URL = https://mergemind.onrender.com
```
*(Use your Render.com URL from Part 1)*

### Step 5: Deploy
1. Click **"Deploy"**
2. Wait 2-3 minutes

### Step 6: Test Frontend
You'll get a URL like: `https://mergemind-xxxx.vercel.app`

---

## Part 3: Connect Frontend ↔ Backend (CORS)

### Step 1: Update CORS on Render
1. Go to your Render dashboard → **mergemind** service
2. Click **"Environment"** → Edit `ALLOWED_ORIGINS`
3. Update to:
   ```
   https://mergemind-xxxx.vercel.app,http://localhost:3000
   ```
4. Render will auto-redeploy

---

## Part 4: Verify Everything Works

Open your Vercel URL and test:
- [ ] Dashboard loads
- [ ] Can create a new run with GitHub issue URL
- [ ] Run status updates via SSE
- [ ] Approval/rejection gates work

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| 404 on `/health` | Check Render logs - is `backend/main.py` in the right location? |
| CORS errors | Make sure `ALLOWED_ORIGINS` matches your exact Vercel URL |
| SSE not streaming | Vercel has 30s timeout - this is expected |
| Build fails | Check `requirements.txt` has all dependencies |

---

## Live URLs (Example)
- **Backend:** `https://mergemind.onrender.com`
- **Frontend:** `https://mergemind-xxxx.vercel.app`
- **API Docs:** `https://mergemind.onrender.com/docs`

