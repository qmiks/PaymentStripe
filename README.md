# FastAPI + Stripe Payment Application

A modern payment processing application built with FastAPI, Stripe, and SQLite. Features include multiple payment methods, admin panel, audit logging, and dynamic configuration.

## 🚀 Features

- **Multiple Payment Methods**: Support for cards, BLIK, Przelewy24, Bancontact, iDEAL, SOFORT, and more
- **Admin Panel**: Secure admin interface for managing Stripe keys and payment methods
- **Audit Logging**: Comprehensive logging of all administrative actions
- **Dynamic Configuration**: Database-backed settings management
- **Modern UI**: Responsive design with real-time payment method selection
- **Security**: JWT authentication, password hashing, and audit trails

## 📋 Prerequisites

- Python 3.8+
- Stripe account with API keys
- Conda (recommended) or pip

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PaymentStripe
   ```

2. **Create and activate conda environment**
   ```bash
   conda create -n paymentstripe python=3.11
   conda activate paymentstripe
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   # Required: Generate a strong secret key
   JWT_SECRET_KEY=your-super-secret-jwt-key-here
   
   # Optional: Fallback Stripe keys (can be set via admin panel)
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
   
   # Optional: App configuration
   APP_BASE_URL=http://localhost:8000
   HOST=0.0.0.0
   PORT=8000
   ENV=dev
   ```

## 🚀 Running the Application

1. **Start the server**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access the application**
   - Main payment page: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   - API documentation: http://localhost:8000/docs

## 🔐 Initial Setup

1. **Access the admin panel** at http://localhost:8000/admin
2. **Login with default credentials**:
   - Username: `admin`
   - Password: `admin123`
3. **Initialize settings** by clicking "Initialize Settings"
4. **Configure Stripe keys** in the admin panel
5. **Change admin password** immediately for security

## 🔒 Security Considerations

### Critical Security Steps

1. **Change JWT Secret Key**
   - Generate a strong secret key: `openssl rand -hex 32`
   - Set it in your `.env` file as `JWT_SECRET_KEY`

2. **Change Default Admin Password**
   - Login to admin panel
   - Update admin password immediately
   - Default credentials are publicly known

3. **Configure Stripe Keys**
   - Use real Stripe keys from your Stripe dashboard
   - Never commit keys to version control

4. **Environment Variables**
   - Use production environment variables
   - Set `ENV=prod` for production

### Production Deployment

1. **Use HTTPS** in production
2. **Set strong passwords** for all admin accounts
3. **Configure proper database** (PostgreSQL recommended for production)
4. **Set up proper logging** and monitoring
5. **Use environment-specific configurations**

## 📁 Project Structure

```
PaymentStripe/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── db.py                # Database setup
│   ├── models.py            # SQLModel database models
│   ├── auth.py              # Authentication utilities
│   ├── routes_checkout.py   # Payment checkout routes
│   ├── routes_orders.py     # Order management routes
│   ├── routes_webhooks.py   # Stripe webhook handling
│   └── routes_admin.py      # Admin panel routes
├── static/
│   ├── index.html           # Main payment page
│   └── admin.html           # Admin panel interface
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── README.md               # This file
```

## 🔧 Configuration

### Payment Methods
Configure available payment methods in the admin panel:
- Credit/Debit Cards
- BLIK (Polish mobile payments)
- Przelewy24 (Polish bank transfers)
- Bancontact (Belgian payments)
- iDEAL (Dutch payments)
- SOFORT (German payments)
- Giropay (German payments)
- EPS (Austrian payments)
- SEPA Direct Debit
- SEPA Credit Transfer

### Currencies
Configure supported currencies in the admin panel:
- PLN (Polish Złoty)
- USD (US Dollar)
- EUR (Euro)
- GBP (British Pound)
- CAD (Canadian Dollar)
- AUD (Australian Dollar)
- CHF (Swiss Franc)
- SEK (Swedish Krona)
- NOK (Norwegian Krone)
- DKK (Danish Krone)

### Stripe Webhook Setup
1. Go to your Stripe Dashboard
2. Navigate to Developers > Webhooks
3. Add endpoint: `https://yourdomain.com/stripe/webhook`
4. Select events: `checkout.session.completed`
5. Copy the webhook secret to admin panel

## 🐳 Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Or build manually**
   ```bash
   docker build -t paymentstripe .
   docker run -p 8000:8000 paymentstripe
   ```

## 📊 API Endpoints

- `GET /` - Main payment page
- `GET /admin` - Admin panel
- `POST /api/checkout/session` - Create payment session
- `GET /api/checkout/payment-methods` - Get available payment methods
- `GET /api/checkout/currencies` - Get available currencies
- `POST /api/admin/login` - Admin login
- `GET /api/admin/settings` - Get settings
- `PUT /api/admin/settings/{key}` - Update setting
- `POST /api/admin/init` - Initialize admin and settings
- `GET /api/admin/audit-logs` - Get audit logs
- `POST /stripe/webhook` - Stripe webhook handler

## 🛠️ Development

### Adding New Payment Methods
1. Update `app/routes_checkout.py` payment method mapping
2. Update `static/admin.html` available methods list
3. Update `static/index.html` fallback methods

### Database Migrations
The application uses SQLModel with automatic table creation. For schema changes:
1. Update models in `app/models.py`
2. Restart the application
3. Tables will be recreated automatically

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure conda environment is activated
   - Run `pip install -r requirements.txt`

2. **Stripe webhook errors**
   - Verify webhook secret in admin panel
   - Check webhook endpoint URL in Stripe dashboard

3. **Admin panel not loading settings**
   - Click "Initialize Settings" in admin panel
   - Check browser console for errors

4. **Payment methods not showing**
   - Configure payment methods in admin panel
   - Check browser console for API errors

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## ⚠️ Disclaimer

This is a demo application. For production use:
- Implement proper security measures
- Use production-grade databases
- Set up proper monitoring and logging
- Follow security best practices
- Test thoroughly before deployment