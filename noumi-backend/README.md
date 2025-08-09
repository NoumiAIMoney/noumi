# Noumi Backend (Go)

A high-performance Go backend for the Noumi financial planning application, built with Gin web framework and PostgreSQL.

## Project Structure

```
noumi-backend/
├── cmd/
│   └── server/
│       └── main.go                 # Application entry point
├── internal/
│   ├── api/
│   │   ├── handlers/              # HTTP handlers for each endpoint
│   │   ├── middleware/            # Authentication, CORS, logging
│   │   └── routes/                # Route definitions
│   ├── config/
│   │   └── config.go              # Configuration management
│   ├── database/
│   │   ├── migrations/            # SQL migration files
│   │   ├── models/                # Database models
│   │   └── repository/            # Data access layer
│   ├── services/
│   │   ├── analytics/             # Spending analysis logic
│   │   ├── anomaly/               # Anomaly detection
│   │   ├── llm/                   # OpenAI integration
│   │   └── auth/                  # Authentication service
│   └── utils/
│       ├── logger/                # Structured logging
│       └── validator/             # Request validation
├── .env.example                   # Environment variables template
├── go.mod                         # Go module definition
└── README.md                      # This file
```

## Getting Started

### Prerequisites

- Go 1.21 or higher
- PostgreSQL 15 or higher
- OpenAI API key (for LLM features)

### Installation

1. Clone the repository and navigate to the backend directory:
   ```bash
   cd noumi-backend
   ```

2. Copy the environment variables template:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` file with your configuration values, especially:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `JWT_SECRET`: A secure secret for JWT token signing

4. Install dependencies:
   ```bash
   go mod tidy
   ```

### Running the Application

1. Start the server:
   ```bash
   go run cmd/server/main.go
   ```

2. The server will start on `http://localhost:8080` by default.

3. Check the health endpoint:
   ```bash
   curl http://localhost:8080/health
   ```

### API Endpoints

- `GET /health` - Health check endpoint
- `GET /api/v1/status` - API status endpoint

More endpoints will be added as development progresses.

## Configuration

The application uses environment variables for configuration. See `.env.example` for all available options.

Key configuration sections:
- **Server**: Port, host, timeouts
- **Database**: PostgreSQL connection and pool settings
- **OpenAI**: API key and model configuration
- **Auth**: JWT secret and token expiry settings
- **Logging**: Log level and format

## Development

### Building

```bash
go build -o bin/server cmd/server/main.go
```

### Running Tests

```bash
go test ./...
```

### Code Structure

This project follows clean architecture principles:
- **cmd/**: Application entry points
- **internal/**: Private application code
- **internal/api/**: HTTP layer (handlers, middleware, routes)
- **internal/services/**: Business logic layer
- **internal/database/**: Data access layer
- **internal/utils/**: Shared utilities

## License

This project is part of the Noumi financial planning application.