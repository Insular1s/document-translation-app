# Deployment Guide - Document Translation App

This guide will help you deploy the Document Translation App with the backend on Render and the frontend on Vercel.

## Prerequisites

- GitHub account
- Render account (free tier available at https://render.com)
- Vercel account (free tier available at https://vercel.com)
- Azure Translator API key
- OpenRouter API key

---

## Part 1: Deploy Backend to Render

### Step 1: Push Code to GitHub

1. Initialize git repository (if not already done):
```bash
cd document-translation-app
git init
git add .
git commit -m "Initial commit - ready for deployment"
```

2. Create a new repository on GitHub (https://github.com/new)
   - Name: `document-translation-app`
   - Make it public or private (your choice)
   - Don't initialize with README (we already have code)

3. Push to GitHub:
```bash
git remote add origin https://github.com/YOUR_USERNAME/document-translation-app.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend on Render

1. Go to https://render.com and sign in/sign up

2. Click "New +" → "Web Service"

3. Connect your GitHub repository:
   - Click "Connect account" if first time
   - Select your `document-translation-app` repository
   - Click "Connect"

4. Configure the web service:
   - **Name**: `document-translation-backend` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free (or paid if you prefer)

5. Add Environment Variables:
   Click "Advanced" → "Add Environment Variable"
   
   Add these variables:
   ```
   AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com/
   AZURE_TRANSLATOR_KEY=your_azure_key_here
   AZURE_TRANSLATOR_REGION=japaneast
   OPENROUTER_API_URL=https://openrouter.ai/api/v1/chat/completions
   OPENROUTER_API_KEY=your_openrouter_key_here
   USE_LLM_ENHANCEMENT=true
   FRONTEND_URL=https://your-app-name.vercel.app
   ```
   
   **Important**: Replace the API keys with your actual keys!
   Note: We'll update FRONTEND_URL after deploying the frontend

6. Click "Create Web Service"

7. Wait for deployment (usually 2-5 minutes)
   - You'll see build logs in real-time
   - Once complete, you'll get a URL like: `https://document-translation-backend.onrender.com`

8. **Save this URL** - you'll need it for the frontend!

9. Test the backend:
   - Open: `https://document-translation-backend.onrender.com/health`
   - Should see: `{"status": "healthy"}`
   - Open: `https://document-translation-backend.onrender.com/docs`
   - Should see the API documentation

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Configure Environment Variable Locally

1. Create `.env.production` in the `frontend` folder:
```bash
cd frontend
echo VITE_API_URL=https://document-translation-backend.onrender.com > .env.production
```

Replace `document-translation-backend.onrender.com` with your actual Render backend URL!

2. Test locally with production settings:
```bash
npm run build
npm run preview
```

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI (Recommended)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy from frontend directory:
```bash
cd frontend
vercel
```

4. Follow the prompts:
   - Set up and deploy? **Y**
   - Which scope? (Choose your account)
   - Link to existing project? **N**
   - Project name? `document-translation-app` (or your choice)
   - In which directory is your code located? **.**
   - Want to override settings? **N**

5. Add environment variable:
```bash
vercel env add VITE_API_URL production
```
Enter your backend URL: `https://document-translation-backend.onrender.com`

6. Deploy to production:
```bash
vercel --prod
```

7. You'll get a URL like: `https://document-translation-app.vercel.app`

#### Option B: Using Vercel Dashboard (Alternative)

1. Go to https://vercel.com and sign in

2. Click "Add New..." → "Project"

3. Import your GitHub repository:
   - Click "Import" on your repository
   - Or enter the repository URL

4. Configure project:
   - **Project Name**: `document-translation-app`
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. Add Environment Variable:
   - Click "Environment Variables"
   - Name: `VITE_API_URL`
   - Value: `https://document-translation-backend.onrender.com` (your backend URL)
   - Environments: Production, Preview, Development (select all)

6. Click "Deploy"

7. Wait for deployment (usually 1-2 minutes)

8. You'll get a URL like: `https://document-translation-app.vercel.app`

---

## Part 3: Update Backend CORS Settings

Now that you have your frontend URL, update the backend:

1. Go back to Render dashboard

2. Click on your backend service

3. Go to "Environment" tab

4. Update the `FRONTEND_URL` variable:
   - Value: `https://document-translation-app.vercel.app` (your actual Vercel URL)

5. Click "Save Changes"

6. Render will automatically redeploy your backend

---

## Part 4: Test the Deployment

1. Open your Vercel URL: `https://document-translation-app.vercel.app`

2. Test the full workflow:
   - Upload a PowerPoint file
   - Select target language
   - Choose LLM model (optional)
   - Click translate
   - Review and edit translations
   - Preview slides
   - Download final document

3. Check browser console for errors (F12 → Console)

4. If you see CORS errors:
   - Double-check FRONTEND_URL in Render
   - Make sure it matches your Vercel URL exactly
   - Wait for Render to finish redeploying

---

## Troubleshooting

### Backend Issues

**Problem**: Build fails on Render
- Check `runtime.txt` has `python-3.12.0`
- Check `requirements.txt` is in `backend` folder
- Check build logs for specific error

**Problem**: Backend starts but crashes
- Check environment variables are set correctly
- Check logs in Render dashboard
- Make sure API keys are valid

**Problem**: "Module not found" errors
- Make sure all dependencies are in `requirements.txt`
- Redeploy with "Clear build cache" option

### Frontend Issues

**Problem**: API calls fail
- Check `VITE_API_URL` is set correctly in Vercel
- Make sure it includes `https://` and no trailing slash
- Check Network tab in browser DevTools

**Problem**: CORS errors
- Update `FRONTEND_URL` in Render backend
- Make sure it matches your Vercel URL exactly
- Wait for backend to redeploy

**Problem**: Slide preview images don't load
- Check if Aspose.Slides is installed on backend
- Check backend logs for errors
- Try accessing slide preview URL directly

### Performance Issues

**Problem**: Render backend is slow
- Free tier spins down after inactivity
- First request after idle takes 30-60 seconds
- Consider upgrading to paid tier for always-on service

**Problem**: Large files timeout
- Increase timeout settings
- Consider upgrading Render instance
- Optimize file processing

---

## Monitoring & Maintenance

### Backend (Render)

1. Check logs:
   - Go to Render dashboard
   - Click on your service
   - Click "Logs" tab

2. Monitor health:
   - Check `/health` endpoint regularly
   - Set up uptime monitoring (UptimeRobot, Pingdom, etc.)

3. Updates:
   - Auto-deploys on git push to main branch
   - Can manually redeploy from dashboard

### Frontend (Vercel)

1. Check deployments:
   - Go to Vercel dashboard
   - Click on your project
   - See all deployments and logs

2. Analytics:
   - Vercel provides analytics for free
   - Check page views, performance, etc.

3. Updates:
   - Auto-deploys on git push to main branch
   - Preview deployments for pull requests

---

## Cost Estimation

### Free Tier Limits

**Render (Backend)**:
- Free tier: 750 hours/month
- Spins down after 15 min of inactivity
- 512 MB RAM
- Shared CPU
- Good for: Testing, small projects

**Vercel (Frontend)**:
- Free tier: Unlimited bandwidth
- 100 GB bandwidth/month
- Unlimited deployments
- Good for: Most small to medium projects

### When to Upgrade

- Backend receives consistent traffic → Render paid ($7+/month)
- Need faster response times → Render paid tier
- Heavy file processing → Render scaled instance
- High traffic → Both platforms have scaling options

---

## Security Checklist

- [ ] Remove API keys from code (use environment variables only)
- [ ] Set up proper CORS (only allow your frontend domain)
- [ ] Use HTTPS for all communications (Render & Vercel provide this)
- [ ] Don't commit `.env` files to git
- [ ] Rotate API keys periodically
- [ ] Monitor usage and set up billing alerts
- [ ] Keep dependencies updated
- [ ] Review logs for suspicious activity

---

## Next Steps

After successful deployment:

1. **Custom Domain** (Optional):
   - Vercel: Add custom domain in project settings
   - Render: Add custom domain in service settings
   - Update DNS records as instructed

2. **Set Up Monitoring**:
   - UptimeRobot for backend health checks
   - Sentry for error tracking
   - Google Analytics for frontend

3. **Improve Performance**:
   - Add caching headers
   - Optimize images and assets
   - Consider CDN for static files

4. **Backup Strategy**:
   - Render doesn't persist files (use external storage)
   - Consider AWS S3 or Cloudinary for uploads
   - Keep git repository backed up

---

## Support

If you encounter issues:

1. Check this guide first
2. Review error logs in Render/Vercel
3. Check browser console (F12)
4. Verify all environment variables
5. Test API endpoints directly

For platform-specific issues:
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs

---

Good luck with your deployment! 🚀
