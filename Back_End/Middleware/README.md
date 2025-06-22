# Noumi FastAPI Backend

A personalized weekly planning app backend built with FastAPI, designed to integrate with LLM and ML services for personalized user experiences.

## Features

- **Authentication**: User registration and login with JWT tokens
- **Spending Tracking**: Track and categorize expenses
- **Weekly Planning**: AI-powered weekly plan generation
- **Weekly Recaps**: Automated insights and achievements summary
- **User Preferences**: Customizable settings for personalization
- **AI Integration**: Endpoints ready for ML/AI personalization

## Quick Start

### 1. Install Dependencies

```bash
cd Back_End
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the example environment file and configure your settings:

```bash
cd Middleware
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start the Server

Option 1 - Using the startup script:
```bash
python start_server.py
```

Option 2 - Using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the API

- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info

### Spending
- `GET /spending/total` - Get spending totals
- `GET /spending/categories` - Get spending categories
- `POST /spending` - Add new spending record

### Weekly Planning
- `GET /plans/weekly` - Get weekly plans
- `POST /plans/weekly` - Create new weekly plan

### Weekly Recaps
- `GET /recaps/weekly` - Get weekly recaps
- `POST /recaps/weekly/generate` - Generate AI-powered recap

### User Preferences
- `GET /users/preferences` - Get user preferences
- `PUT /users/preferences` - Update user preferences

### AI/ML
- `POST /ai/personalize` - Get personalization insights

## Development

### Project Structure

```
Back_End/Middleware/
├── main.py              # FastAPI application
├── start_server.py      # Server startup script
├── .env.example         # Environment variables template
├── .env                 # Your environment variables (create this)
└── README.md           # This file
```

### Testing the API

You can test the API using the interactive documentation at http://localhost:8000/docs or with curl:

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123", "name": "Test User"}'

# Get spending data (requires authentication)
curl -X GET "http://localhost:8000/spending/total" \
     -H "Authorization: Bearer your-token-here"
```

## Next Steps

1. **Database Integration**: Connect to a real database (PostgreSQL recommended)
2. **Authentication**: Implement proper JWT token generation and validation
3. **ML/AI Integration**: Connect to your ML models and LLM services
4. **Plaid Integration**: Connect to existing Plaid service for spending data
5. **Production Deployment**: Configure for production environment

## Configuration

Key environment variables in `.env`:

- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 8000)
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `DATABASE_URL`: Database connection string
- `CORS_ORIGINS`: Allowed CORS origins for frontend

## Architecture Notes

This FastAPI backend is designed to:

- Serve as middleware between your React Native frontend and various services
- Provide mock responses initially, with TODO comments for real implementations
- Scale easily with additional endpoints and services
- Integrate with your existing ML models and database services
- Handle CORS for React Native development

The current implementation returns mock data to allow immediate frontend-backend communication testing.
