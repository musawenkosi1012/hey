# Render Deployment Guide

## Overview
This guide provides complete instructions for deploying ChroniSense to Render with one-click deployment.

## Prerequisites
- GitHub account with repository access
- Render account (free tier available)

## Deployment Steps

### Option 1: One-Click Deployment

1. **Click the Deploy Button**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select the `musawenkosi1012/hey` repository
   - Click "Apply"

2. **Automatic Setup**
   - Render will automatically:
     - Read the `render.yaml` configuration
     - Install Python dependencies from `requirements.txt`
     - Run `build.sh` to initialize the database
     - Start the application with gunicorn

3. **Access Your Application**
   - Once deployed, Render will provide a URL like: `https://chronisense.onrender.com`
   - Visit the URL to access your application

### Option 2: Manual Deployment

1. **Create Web Service**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect to GitHub repository

2. **Configure Service**
   ```
   Name: chronisense
   Region: Oregon (or your preferred region)
   Branch: main
   Runtime: Python 3
   Build Command: ./build.sh
   Start Command: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT wsgi:app
   ```

3. **Set Environment Variables**
   - `SECRET_KEY`: Auto-generate or set custom value
   - `DATABASE_URL`: sqlite:///chronisense.db
   - `FLASK_ENV`: production
   - `LOG_LEVEL`: INFO
   - `PYTHON_VERSION`: 3.12.3

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

## Environment Variables

### Required Variables
- **SECRET_KEY**: Flask secret key for session security (auto-generated on Render)
- **DATABASE_URL**: Database connection string (default: SQLite)

### Optional Variables
- **OPENAI_API_KEY**: OpenAI API key for AI chatbot (optional)
- **TWILIO_ACCOUNT_SID**: Twilio account SID for SMS alerts (optional)
- **TWILIO_AUTH_TOKEN**: Twilio auth token (optional)
- **LOG_LEVEL**: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **FLASK_ENV**: Environment mode (production recommended)

## Database Configuration

### SQLite (Default)
- Database is automatically created during build
- Stored in `instance/chronisense.db`
- Perfect for development and small-scale production
- **Note**: On Render's free tier, database resets on each deployment

### PostgreSQL (Recommended for Production)
To use PostgreSQL instead of SQLite:

1. **Create PostgreSQL Database**
   - In Render Dashboard, create a new PostgreSQL database
   - Copy the Internal Database URL

2. **Update Environment Variable**
   - Set `DATABASE_URL` to your PostgreSQL connection string
   - Format: `postgresql://user:password@host:port/database`

3. **Update requirements.txt** (if not already present)
   ```
   psycopg2-binary==2.9.9
   ```

4. **Redeploy**
   - Database tables will be created automatically

## Health Check

The application includes a health check endpoint at `/api/health`

```bash
curl https://your-app.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "ChroniSense API",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00"
}
```

## Demo Accounts

After deployment, the following demo accounts are available:

- **Patient**: 
  - Username: `patient`
  - Password: `password123`

- **Doctor**: 
  - Username: `doctor`
  - Password: `password123`

- **Caregiver**: 
  - Username: `caregiver`
  - Password: `password123`

**⚠️ IMPORTANT**: Change these passwords in production!

## Testing Deployment

### 1. Test Web Interface
```bash
curl https://your-app.onrender.com/
```

### 2. Test API Health
```bash
curl https://your-app.onrender.com/api/health
```

### 3. Test Login
```bash
curl -X POST https://your-app.onrender.com/auth/login \
  -d "username=patient&password=password123" \
  -c cookies.txt
```

### 4. Test API Endpoint
```bash
curl -b cookies.txt https://your-app.onrender.com/api/vitals/1
```

## Monitoring

### Logs
- Access logs in Render Dashboard → Your Service → Logs
- Real-time log streaming available
- Logs show all application activity

### Metrics
- CPU and Memory usage available in Render Dashboard
- Response times and request counts
- Health check status

## Troubleshooting

### Build Fails
- Check `build.sh` is executable: `chmod +x build.sh`
- Verify all dependencies in `requirements.txt`
- Check Python version compatibility

### Application Won't Start
- Check `wsgi.py` exists and is correct
- Verify gunicorn is installed
- Check environment variables are set

### Database Issues
- Verify `DATABASE_URL` is correct
- Check `init_db.py` runs successfully
- Ensure database tables are created

### 500 Errors
- Check application logs in Render Dashboard
- Verify all environment variables
- Check database connectivity

## Performance Optimization

### Gunicorn Configuration
Current configuration:
```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT wsgi:app
```

For higher traffic:
```bash
gunicorn --worker-class eventlet -w 2 --bind 0.0.0.0:$PORT wsgi:app
```

### Caching
Consider adding Redis for session storage:
1. Create Redis instance in Render
2. Add `redis` to requirements.txt
3. Configure Flask-Session with Redis backend

## Security Best Practices

1. **Change Default Passwords**
   - Update demo account passwords immediately
   - Use strong, unique passwords

2. **Environment Variables**
   - Never commit `.env` to repository
   - Use Render's environment variable management

3. **HTTPS**
   - Render provides free SSL certificates
   - All traffic is encrypted by default

4. **Database Backups**
   - If using PostgreSQL, enable automatic backups in Render
   - SQLite: implement custom backup strategy

## Scaling

### Free Tier Limitations
- Sleeps after 15 minutes of inactivity
- 750 hours per month
- Limited CPU and memory

### Upgrading
- **Starter Plan**: No sleep, custom domains
- **Professional Plan**: Higher resources, auto-scaling

## Support

For issues or questions:
1. Check logs in Render Dashboard
2. Review `QUICK_START.md` for system validation
3. Run `validate_system.py` locally to test
4. Create GitHub issue for bugs

## Next Steps

After successful deployment:
1. Test all features with demo accounts
2. Configure custom domain (optional)
3. Set up monitoring and alerts
4. Review and update security settings
5. Plan for database backups
6. Consider upgrading to paid plan for production use

---

**Deployment Status**: ✅ Ready for one-click deployment
**Last Updated**: 2025-09-30
**Platform**: Render
