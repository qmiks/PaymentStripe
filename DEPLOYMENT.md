# 🚀 Deployment Guide

This guide explains how to deploy the Stripe Payment Application to production environments.

## 📋 Prerequisites

- Python 3.8+
- pip or conda
- Stripe account with API keys
- Web server (nginx, Apache) for production
- SSL certificate for HTTPS

## 🔧 Installation Steps

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd PaymentStripe
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
Create a `.env` file in the project root:
```bash
# Database
DATABASE_URL=sqlite:///./app.db

# JWT Secret (generate a secure random string)
JWT_SECRET_KEY=your-super-secret-jwt-key-here

# Stripe Keys (get these from your Stripe dashboard)
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Application Settings
APP_BASE_URL=https://yourdomain.com
```

### 4. Initialize Database
Run the database initialization script:
```bash
python init_db.py
```

This will:
- Create the database file
- Create all tables
- Create admin user (username: `admin`, password: `admin123`)
- Set up default settings

### 5. Start the Application

#### Development
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🌐 Production Deployment

### Using Gunicorn (Recommended)
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker
```bash
# Build the image
docker build -t stripe-payment-app .

# Run the container
docker run -p 8000:8000 -v $(pwd)/app.db:/app/app.db stripe-payment-app
```

### Using Docker Compose
```bash
docker-compose up -d
```

## 🔒 Security Configuration

### 1. Change Default Admin Password
1. Login to admin panel: `https://yourdomain.com/admin`
2. Use default credentials: `admin` / `admin123`
3. Update admin password in settings

### 2. Configure Stripe Keys
1. Go to admin panel → Settings
2. Update `STRIPE_SECRET_KEY` with your live Stripe secret key
3. Update `STRIPE_PUBLISHABLE_KEY` with your live Stripe publishable key
4. Update `STRIPE_WEBHOOK_SECRET` with your webhook secret

### 3. Set Up Stripe Webhooks
1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://yourdomain.com/stripe/webhook`
3. Select events: `checkout.session.completed`, `payment_intent.payment_failed`
4. Copy the webhook secret to your admin panel settings

## 📊 Monitoring and Logs

### Audit Trail
- All admin actions are logged in the audit trail
- Payment attempts and status changes are tracked
- Access via admin panel → Audit Logs

### Application Logs
```bash
# View application logs
tail -f logs/app.log

# View error logs
tail -f logs/error.log
```

## 🔄 Database Management

### Backup Database
```bash
# Create backup
cp app.db app.db.backup.$(date +%Y%m%d_%H%M%S)

# Or use SQLite backup command
sqlite3 app.db ".backup app.db.backup"
```

### Restore Database
```bash
# Stop the application
# Replace the database file
cp app.db.backup app.db
# Restart the application
```

### Database Migration
If you need to update the database schema:
1. Stop the application
2. Backup current database
3. Delete `app.db`
4. Restart application (tables will be recreated)
5. Run `python init_db.py` to reinitialize

## 🚨 Troubleshooting

### Common Issues

1. **Database Locked**
   ```bash
   # Stop all Python processes
   pkill -f python
   # Or restart the server
   ```

2. **Permission Denied**
   ```bash
   # Ensure proper file permissions
   chmod 755 app.db
   chown www-data:www-data app.db
   ```

3. **Stripe Webhook Failures**
   - Check webhook secret in admin panel
   - Verify webhook endpoint URL in Stripe dashboard
   - Check application logs for errors

4. **Admin Login Issues**
   - Run `python init_db.py` to recreate admin user
   - Check JWT_SECRET_KEY environment variable

### Health Check
```bash
# Test if application is running
curl http://localhost:8000/

# Test admin API
curl http://localhost:8000/api/admin/settings
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_status ON "order"(status);
```

### Application Optimization
- Use multiple workers with Gunicorn
- Enable database connection pooling
- Use CDN for static files
- Enable compression

## 🔐 Security Checklist

- [ ] Changed default admin password
- [ ] Updated Stripe keys to live keys
- [ ] Configured HTTPS/SSL
- [ ] Set secure JWT secret
- [ ] Configured firewall rules
- [ ] Set up monitoring and alerts
- [ ] Regular database backups
- [ ] Updated dependencies regularly

## 📞 Support

For deployment issues:
1. Check application logs
2. Review audit trail in admin panel
3. Verify environment variables
4. Test with Stripe test keys first
