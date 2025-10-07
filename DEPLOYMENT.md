# Deployment Guide

This guide will help you deploy the NCB KYC Document Processing System to production.

## 🚀 **Quick Deployment (Recommended)**

### Frontend: Deploy to Vercel
1. **Fork this repository** on GitHub
2. **Go to [Vercel](https://vercel.com)** and sign in
3. **Click "New Project"**
4. **Import your forked repository**
5. **Configure build settings**:
   - Framework Preset: `Vite`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
6. **Add environment variable**:
   - Key: `VITE_API_BASE`
   - Value: `https://your-backend-url.railway.app` (you'll get this after backend deployment)
7. **Deploy!**

### Backend: Deploy to Railway
1. **Go to [Railway](https://railway.app)** and sign in
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose your forked repository**
5. **Add environment variables**:
   ```
   PROJECT_ID=your-project-id
   LOCATION=us
   CUSTOM_EXTRACTOR_ID=your-custom-extractor-processor-id
   CUSTOM_EXTRACTOR_VERSION_ID=your-custom-extractor-version-id
   ```
6. **Deploy!**

## 🔧 **Alternative Backend Hosts**

### Render
1. Go to [Render](https://render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m src.api.main`
   - Environment: `Python 3`

### Heroku
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: python -m src.api.main
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set PROJECT_ID=your-project-id
   heroku config:set LOCATION=us
   heroku config:set CUSTOM_EXTRACTOR_ID=your-custom-extractor-processor-id
   heroku config:set CUSTOM_EXTRACTOR_VERSION_ID=your-custom-extractor-version-id
   git push heroku main
   ```

## 🔑 **Google Cloud Setup**

### 1. Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to IAM & Admin > Service Accounts
3. Click "Create Service Account"
4. Name: `kyc-extraction-service`
5. Grant roles:
   - Document AI API User
   - Document AI Editor

### 2. Create Service Account Key
1. Click on your service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose JSON format
5. Download the key file

### 3. Set Up Document AI
1. Enable Document AI API
2. Create a custom extractor processor
3. Note down the Processor ID and Version ID
4. Add these to your environment variables

## 🌐 **Domain Setup (Optional)**

### Custom Domain for Frontend
1. In Vercel dashboard, go to your project
2. Click "Settings" > "Domains"
3. Add your custom domain
4. Update DNS records as instructed

### Custom Domain for Backend
1. In Railway/Render dashboard
2. Go to Settings > Domains
3. Add custom domain
4. Update DNS records

## 🔒 **Security Considerations**

1. **Environment Variables**: Never commit `.env` files
2. **API Keys**: Use environment variables for all secrets
3. **CORS**: Configure CORS for your production domains
4. **Rate Limiting**: Consider adding rate limiting for production
5. **Monitoring**: Set up error monitoring (Sentry, etc.)

## 📊 **Monitoring & Analytics**

### Frontend Monitoring
- Vercel Analytics (built-in)
- Google Analytics
- Sentry for error tracking

### Backend Monitoring
- Railway/Render built-in metrics
- Google Cloud Monitoring
- Application logs

## 🚨 **Troubleshooting**

### Common Issues

1. **CORS Errors**
   - Check `VITE_API_BASE` environment variable
   - Ensure backend CORS is configured for your domain

2. **Google Cloud Authentication**
   - Verify service account key is correct
   - Check Document AI API is enabled
   - Ensure processor ID and version ID are correct

3. **Build Failures**
   - Check Node.js version (18+)
   - Verify all dependencies are installed
   - Check build logs for specific errors

4. **API Timeouts**
   - Document AI processing can take 20+ seconds
   - Consider increasing timeout limits
   - Implement proper loading states

## 📈 **Performance Optimization**

1. **Frontend**
   - Enable Vercel Edge Functions
   - Use CDN for static assets
   - Implement lazy loading

2. **Backend**
   - Use connection pooling
   - Implement caching
   - Optimize Document AI calls

## 🔄 **Updates & Maintenance**

1. **Regular Updates**
   - Keep dependencies updated
   - Monitor security advisories
   - Test with new Document AI versions

2. **Backup Strategy**
   - Backup environment variables
   - Document configuration changes
   - Keep service account keys secure

## 📞 **Support**

- GitHub Issues for bug reports
- Documentation in README.md
- API documentation at `/docs` endpoint
