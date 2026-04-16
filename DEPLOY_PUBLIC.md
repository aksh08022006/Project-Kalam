# 🚀 DEPLOY PROJECT KALAM TO PUBLIC URL

Your Project Kalam Phase 1 is ready to deploy publicly. Choose one of these options:

---

## **OPTION 1: Render.com (Recommended - Free & Easy)**

### Step 1: Go to Render
Visit: https://render.com

### Step 2: Connect GitHub
1. Click "New +" → "Web Service"
2. Select your GitHub repository: `aksh08022006/Project-Kalam`
3. Authorize Render to access your GitHub

### Step 3: Configure Service
- **Name:** `project-kalam`
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn simple_app:app`
- **Plan:** Free (you'll get a free URL)

### Step 4: Deploy
Click "Create Web Service" and wait 2-3 minutes for deployment.

**Your public URL will be:** `https://project-kalam-xxxxx.onrender.com`

---

## **OPTION 2: Railway.app (Free Tier)**

### Step 1: Go to Railway
Visit: https://railway.app

### Step 2: Deploy from GitHub
1. Click "New Project" → "Deploy from GitHub repo"
2. Select `aksh08022006/Project-Kalam`

### Step 3: Railway Auto-Detects
Railway will detect it's a Python/Flask app and auto-configure

### Step 4: Get Your URL
Once deployed, your URL will be in the Railway dashboard

**Your public URL will be:** `https://project-kalam-production.up.railway.app`

---

## **OPTION 3: Heroku (Free Tier Ended - Use Render/Railway)**

Heroku's free tier is discontinued. Use Render or Railway instead.

---

## **OPTION 4: ngrok (Quick 5-Minute Demo)**

If you just want a temporary public URL quickly:

```bash
# Install ngrok
brew install ngrok

# Authenticate (sign up at ngrok.com first)
ngrok config add-authtoken YOUR_TOKEN

# Start tunnel to localhost:5000
ngrok http 5000
```

You'll get a URL like: `https://abc123-456-789.ngrok.io`

**Note:** This is temporary (expires after 2 hours on free plan)

---

## **RECOMMENDED: Render.com**

### Why Render?
- ✅ Free tier available
- ✅ Automatic GitHub integration
- ✅ Persistent URL (no expiration)
- ✅ SSL/HTTPS included
- ✅ Auto-deploys on git push
- ✅ Simple dashboard

### Quick Steps:
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Select `aksh08022006/Project-Kalam`
5. Keep default settings (we've configured render.yaml)
6. Click "Create Web Service"
7. Wait 2-3 minutes
8. Get your public URL from dashboard

**That's it!** Your app will be live at a public URL you can submit.

---

## **After Deployment**

### Test Your Deployed App

Once deployed, test with these commands:

```bash
# Replace with your actual URL
YOUR_URL="https://project-kalam-xxxxx.onrender.com"

# Health check
curl $YOUR_URL/health

# Get all schemes
curl $YOUR_URL/schemes

# Get specific scheme
curl $YOUR_URL/scheme/pm_kisan
```

### Share Your Deployment

You can now share:
- **Live URL:** https://project-kalam-xxxxx.onrender.com
- **GitHub Repo:** https://github.com/aksh08022006/Project-Kalam
- **API Documentation:** https://project-kalam-xxxxx.onrender.com (or share LIVE_DEPLOYMENT.md)

---

## **Project Status for Submission**

✅ **What you can submit:**
- Live API at `https://project-kalam-xxxxx.onrender.com`
- 10 government schemes ready to serve
- 4 working API endpoints
- Production-ready Flask application
- Docker support (Dockerfile + docker-compose.yml)
- Full documentation
- Source code on GitHub

✅ **Live Endpoints:**
- `GET /health` - Server status
- `GET /schemes` - List all schemes
- `GET /scheme/{id}` - Get specific scheme
- `GET /` - Homepage

---

## **Environment Variables (If Needed)**

If you need to set environment variables on Render:

1. Go to Render Dashboard
2. Select your service
3. Go to "Environment" tab
4. Add variables:
   - `ANTHROPIC_API_KEY` (if using AI features)
   - `SECRET_KEY` (if needed)

---

## **Troubleshooting**

**Build fails?**
- Check requirements.txt is correct
- Verify render.yaml exists

**App crashes after deploy?**
- Check logs in Render dashboard
- Ensure simple_app.py runs without errors

**404 on /schemes endpoint?**
- Verify data/schemes/extracted_schemes.json exists in repo
- Check git push was successful

---

## **Next Steps**

1. **Choose deployment option** (Render recommended)
2. **Follow the steps** for your choice
3. **Wait for deployment** (2-5 minutes)
4. **Test your live URL** with curl commands above
5. **Share the URL** for submission

---

**Current GitHub Repo:** https://github.com/aksh08022006/Project-Kalam

**Latest Commit:** `159c3b0` (render.yaml + gunicorn)

**Ready to deploy! Choose Option 1 (Render) and follow the steps above.** 🚀
