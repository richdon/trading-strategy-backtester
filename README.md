# Trading Strategy Backtester

A Flask-based REST API for backtesting trading strategies with PostgreSQL database and Docker support.

## Features

- User authentication with JWT
- Multiple trading strategies support (MACD, Moving Average)
- PostgreSQL database for data persistence
- Swagger UI documentation
- Docker and Docker Compose setup
- Automated backtesting with customizable parameters
- Performance metrics calculation

## Project Structure

```
trading-strategy-backtester/
├── app.py                 # Main application entry point
├── auth.py               # Authentication routes and logic
├── backtest.py           # Backtesting routes and logic
├── config.py             # Configuration settings
├── database_utils.py     # Database utilities
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Docker container configuration
├── extensions.py        # Flask extensions initialization
├── models.py            # Database models
├── models_docs.py       # Swagger documentation models
├── namespace_auth.py    # Auth namespace definitions
├── namespace_backspace.py # Backtest namespace definitions
├── requirements.txt     # Python dependencies
├── routes.py           # API route definitions
├── strategies.py       # Trading strategy implementations
└── .env               # Environment variables (create from .env.example)
```

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (handled by Docker)

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/richdon/trading-strategy-backtester
cd trading-strategy-backtester
```

2. Create a `.env` file from the template:
```bash
cp .env.example .env
```

3. Update the `.env` file with your configuration:
```env
# Flask Configuration
FLASK_APP=app.py
FLASK_DEBUG=True

# PostgreSQL Database Configuration
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<db_name>
POSTGRES_HOST=db
POSTGRES_PORT=5432

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=5001
```

4. Build and start the containers:
```bash
docker-compose up --build
```

The application will be available at:
- API: http://localhost:5001/api
- Swagger Documentation: http://localhost:5001/api/docs

## API Documentation

The API documentation is available through Swagger UI. After starting the application, visit `http://localhost:5001/api/docs` to:
- View all available endpoints
- Test API endpoints directly
- See request/response models
- Download OpenAPI specification

### Main Endpoints

#### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and receive JWT token
- `GET /api/auth/profile` - Get current user profile
- `PUT /api/auth/profile` - Update user profile

#### Backtesting
- `POST /api/backtest` - Execute a new backtest
- `GET /api/backtest/list` - List all backtests
- `GET /api/backtest/greatest-return` - Get best performing backtest

## Development

For local development:

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: `.venv\Scripts\activate`
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start only the database:
```bash
docker-compose up db -d
```

4. Run the Flask application:
```bash
flask run
```

## Testing Endpoints

Using curl:

1. Register a new user:
```bash
curl -X POST http://localhost:5001/api/auth/register \
-H "Content-Type: application/json" \
-d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
}'
```

2. Login:
```bash
curl -X POST http://localhost:5001/api/auth/login \
-H "Content-Type: application/json" \
-d '{
    "username": "testuser",
    "password": "securepassword123"
}'
```

3. Run a backtest (requires JWT token):
```bash
curl -X POST http://localhost:5001/api/backtest \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
    "strategy": "MACD Crossover",
    "asset": "BTC/USDT",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "interval": "1d",
    "initial_capital": 10000
}'
```

## Database Management

The application includes several database management commands:

```bash
# Recreate database (WARNING: Deletes all data)
docker-compose exec web flask recreate-db

# Create database extensions
docker-compose exec web flask create-extensions

# Create additional indexes
docker-compose exec web flask create-indexes
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
