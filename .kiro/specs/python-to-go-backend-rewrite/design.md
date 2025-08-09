# Design Document

## Overview

This design outlines the migration from the existing Python FastAPI backend to a modern Go Gin backend with full containerization. The new architecture will maintain API compatibility while providing improved performance, better resource utilization, and production-ready deployment capabilities.

The system consists of four main containerized components:
1. **Go Gin Backend** - Core API server with 12 endpoints
2. **PostgreSQL Database** - Primary data store with migrations
3. **Nginx Reverse Proxy** - Load balancing and SSL termination
4. **Migration Tools** - SQLite to PostgreSQL data migration utilities

## Architecture

### High-Level Architecture

```mermaid
graph TB
    Client[Frontend Client] --> Nginx[Nginx Container]
    Nginx --> GoAPI[Go Gin API Container]
    GoAPI --> PostgreSQL[PostgreSQL Container]
    GoAPI --> OpenAI[OpenAI API]
    
    Migration[Migration Container] --> SQLite[Existing SQLite DB]
    Migration --> PostgreSQL
    
    subgraph "Docker Network"
        Nginx
        GoAPI
        PostgreSQL
        Migration
    end
```

### Container Architecture

```mermaid
graph LR
    subgraph "Docker Compose Stack"
        subgraph "Web Tier"
            N[Nginx:alpine]
        end
        
        subgraph "Application Tier"
            G[Go Gin API]
        end
        
        subgraph "Data Tier"
            P[PostgreSQL:15]
            R[Redis:alpine]
        end
        
        subgraph "Migration"
            M[Go Migration Tool]
        end
    end
    
    N --> G
    G --> P
    G --> R
    M --> P
```

### API Layer Design

The Go Gin backend will implement a clean architecture pattern:

```
cmd/
├── server/
│   └── main.go                 # Application entry point
internal/
├── api/
│   ├── handlers/              # HTTP handlers for each endpoint
│   ├── middleware/            # Authentication, CORS, logging
│   └── routes/                # Route definitions
├── config/
│   └── config.go              # Configuration management
├── database/
│   ├── migrations/            # SQL migration files
│   ├── models/                # Database models
│   └── repository/            # Data access layer
├── services/
│   ├── analytics/             # Spending analysis logic
│   ├── anomaly/               # Anomaly detection
│   ├── llm/                   # OpenAI integration
│   └── auth/                  # Authentication service
└── utils/
    ├── logger/                # Structured logging
    └── validator/             # Request validation
```

## Components and Interfaces

### 1. Go Gin API Server

**Core Components:**
- **Router**: Gin router with middleware chain
- **Handlers**: HTTP request handlers for 12 API endpoints
- **Services**: Business logic layer
- **Repository**: Data access abstraction
- **Models**: Data structures and validation

**Key Interfaces:**

```go
// Repository interface for data access
type Repository interface {
    // User operations
    CreateUser(ctx context.Context, user *User) error
    GetUser(ctx context.Context, userID int) (*User, error)
    
    // Goal operations
    CreateGoal(ctx context.Context, goal *Goal) error
    GetUserGoals(ctx context.Context, userID int) ([]*Goal, error)
    
    // Transaction operations
    CreateTransaction(ctx context.Context, txn *Transaction) error
    GetUserTransactions(ctx context.Context, userID int, filters TransactionFilters) ([]*Transaction, error)
    
    // Analytics operations
    GetSpendingByCategory(ctx context.Context, userID int, dateRange DateRange) (map[string]float64, error)
    GetAnomalies(ctx context.Context, userID int, dateRange DateRange) ([]int, error)
}

// LLM service interface
type LLMService interface {
    GenerateWeeklyPlan(ctx context.Context, userProfile UserProfile, transactions []Transaction) (*WeeklyPlan, error)
    GenerateSpendingInsights(ctx context.Context, spendingData SpendingData) ([]Insight, error)
    AnalyzeTrends(ctx context.Context, transactions []Transaction) ([]Trend, error)
}

// Analytics service interface
type AnalyticsService interface {
    DetectAnomalies(ctx context.Context, userID int, dateRange DateRange) ([]int, error)
    CalculateSpendingTrends(ctx context.Context, userID int) ([]SpendingTrend, error)
    GetSpendingStatus(ctx context.Context, userID int) (*SpendingStatus, error)
    CalculateWeeklySavings(ctx context.Context, userID int) (*WeeklySavings, error)
}
```

### 2. Database Layer

**PostgreSQL Schema Design:**

```sql
-- Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    financial_goal VARCHAR(100),
    impulse_triggers JSONB,
    budgeting_score INTEGER,
    plaid_token TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Goals table
CREATE TABLE goals (
    goal_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    goal_name VARCHAR(255) NOT NULL,
    goal_description TEXT,
    goal_amount DECIMAL(12,2) NOT NULL,
    target_date DATE NOT NULL,
    net_monthly_income DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    transaction_id VARCHAR(255) PRIMARY KEY,
    account_id VARCHAR(255) NOT NULL,
    user_id INTEGER REFERENCES users(user_id),
    amount DECIMAL(12,2) NOT NULL,
    date DATE NOT NULL,
    merchant_name VARCHAR(255),
    category VARCHAR(100),
    mcc INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Anomalies table
CREATE TABLE anomalies (
    anomaly_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    transaction_id VARCHAR(255) REFERENCES transactions(transaction_id),
    date DATE NOT NULL,
    is_anomaly BOOLEAN NOT NULL,
    anomaly_score DECIMAL(8,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weekly plans table
CREATE TABLE weekly_plans (
    weekly_plan_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    plan_data JSONB NOT NULL,
    ml_features JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Migration Strategy:**
- Use golang-migrate for schema versioning
- Implement rollback capabilities
- Data transformation scripts for SQLite to PostgreSQL
- Validation scripts to ensure data integrity

### 3. Nginx Reverse Proxy

**Configuration Features:**
- SSL/TLS termination
- Load balancing (future scaling)
- Static file serving
- Request rate limiting
- Health check routing
- CORS handling

**Nginx Configuration Structure:**
```nginx
upstream go_backend {
    server go-api:8080;
}

server {
    listen 80;
    listen 443 ssl;
    
    location /api/ {
        proxy_pass http://go_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /docs {
        proxy_pass http://go_backend;
    }
    
    location /health {
        proxy_pass http://go_backend;
    }
}
```

### 4. OpenAI Integration Service

**LLM Service Implementation:**
- OpenAI GPT-4 API integration
- Prompt engineering for financial insights
- Response caching and rate limiting
- Fallback mechanisms for API failures
- Cost optimization strategies

**Key Features:**
- Weekly plan generation
- Spending trend analysis
- Habit recommendations
- Anomaly explanations

## Data Models

### Core Data Structures

```go
// User represents a user in the system
type User struct {
    UserID          int       `json:"user_id" db:"user_id"`
    Email           string    `json:"email" db:"email" validate:"required,email"`
    PasswordHash    string    `json:"-" db:"password_hash"`
    Name            string    `json:"name" db:"name" validate:"required"`
    FinancialGoal   string    `json:"financial_goal" db:"financial_goal"`
    ImpulseTriggers []string  `json:"impulse_triggers" db:"impulse_triggers"`
    BudgetingScore  int       `json:"budgeting_score" db:"budgeting_score"`
    PlaidToken      string    `json:"-" db:"plaid_token"`
    CreatedAt       time.Time `json:"created_at" db:"created_at"`
}

// Goal represents a financial goal
type Goal struct {
    GoalID            int       `json:"goal_id" db:"goal_id"`
    UserID            int       `json:"user_id" db:"user_id"`
    GoalName          string    `json:"goal_name" db:"goal_name" validate:"required"`
    GoalDescription   string    `json:"goal_description" db:"goal_description"`
    GoalAmount        float64   `json:"goal_amount" db:"goal_amount" validate:"required,gt=0"`
    TargetDate        time.Time `json:"target_date" db:"target_date" validate:"required"`
    NetMonthlyIncome  float64   `json:"net_monthly_income" db:"net_monthly_income"`
    CreatedAt         time.Time `json:"created_at" db:"created_at"`
}

// Transaction represents a financial transaction
type Transaction struct {
    TransactionID string    `json:"transaction_id" db:"transaction_id"`
    AccountID     string    `json:"account_id" db:"account_id"`
    UserID        int       `json:"user_id" db:"user_id"`
    Amount        float64   `json:"amount" db:"amount"`
    Date          time.Time `json:"date" db:"date"`
    MerchantName  string    `json:"merchant_name" db:"merchant_name"`
    Category      string    `json:"category" db:"category"`
    MCC           int       `json:"mcc" db:"mcc"`
    CreatedAt     time.Time `json:"created_at" db:"created_at"`
}

// API Response Models
type QuizSubmission struct {
    GoalName         string    `json:"goal_name" validate:"required"`
    GoalDescription  string    `json:"goal_description" validate:"required"`
    GoalAmount       float64   `json:"goal_amount" validate:"required,gt=0"`
    TargetDate       time.Time `json:"target_date" validate:"required"`
    NetMonthlyIncome float64   `json:"net_monthly_income" validate:"required,gt=0"`
}

type SpendingTrend struct {
    Icon  string `json:"icon"`
    Trend string `json:"trend"`
}

type SpendingCategory struct {
    CategoryName string  `json:"category_name"`
    Amount       float64 `json:"amount"`
    Month        string  `json:"month"`
}

type UserHabit struct {
    HabitID            int    `json:"habit_id"`
    Description        string `json:"habit_description"`
    WeeklyOccurrences  int    `json:"occurrences"`
    StreakCount        int    `json:"streak_count"`
    IsCompleted        bool   `json:"is_completed"`
}
```

## Error Handling

### Error Response Structure

```go
type APIError struct {
    Code    string `json:"code"`
    Message string `json:"message"`
    Details string `json:"details,omitempty"`
}

type ErrorResponse struct {
    Error     APIError `json:"error"`
    RequestID string   `json:"request_id"`
    Timestamp string   `json:"timestamp"`
}
```

### Error Categories

1. **Validation Errors** (400)
   - Invalid request format
   - Missing required fields
   - Invalid data types

2. **Authentication Errors** (401)
   - Invalid JWT token
   - Expired token
   - Missing authorization header

3. **Authorization Errors** (403)
   - Insufficient permissions
   - Resource access denied

4. **Not Found Errors** (404)
   - User not found
   - Goal not found
   - Transaction not found

5. **Server Errors** (500)
   - Database connection failures
   - External API failures
   - Internal processing errors

### Error Handling Middleware

```go
func ErrorHandlerMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()
        
        if len(c.Errors) > 0 {
            err := c.Errors.Last()
            
            var apiErr APIError
            switch e := err.Err.(type) {
            case *ValidationError:
                apiErr = APIError{
                    Code:    "VALIDATION_ERROR",
                    Message: e.Message,
                    Details: e.Details,
                }
                c.JSON(400, ErrorResponse{
                    Error:     apiErr,
                    RequestID: c.GetString("request_id"),
                    Timestamp: time.Now().UTC().Format(time.RFC3339),
                })
            case *DatabaseError:
                apiErr = APIError{
                    Code:    "DATABASE_ERROR",
                    Message: "Internal server error",
                }
                c.JSON(500, ErrorResponse{
                    Error:     apiErr,
                    RequestID: c.GetString("request_id"),
                    Timestamp: time.Now().UTC().Format(time.RFC3339),
                })
            default:
                apiErr = APIError{
                    Code:    "INTERNAL_ERROR",
                    Message: "Internal server error",
                }
                c.JSON(500, ErrorResponse{
                    Error:     apiErr,
                    RequestID: c.GetString("request_id"),
                    Timestamp: time.Now().UTC().Format(time.RFC3339),
                })
            }
        }
    }
}
```

## Testing Strategy

### Testing Pyramid

1. **Unit Tests** (70%)
   - Service layer logic
   - Repository implementations
   - Utility functions
   - Data transformations

2. **Integration Tests** (20%)
   - Database operations
   - External API integrations
   - End-to-end workflows

3. **API Tests** (10%)
   - HTTP endpoint validation
   - OpenAPI specification compliance
   - Authentication flows

### Test Structure

```go
// Unit test example
func TestAnalyticsService_DetectAnomalies(t *testing.T) {
    tests := []struct {
        name           string
        userID         int
        transactions   []Transaction
        expectedCount  int
        expectedError  error
    }{
        {
            name:   "detect high spending anomalies",
            userID: 1,
            transactions: []Transaction{
                {Amount: -500.00, Category: "Food"},
                {Amount: -50.00, Category: "Food"},
                {Amount: -45.00, Category: "Food"},
            },
            expectedCount: 1,
            expectedError: nil,
        },
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // Test implementation
        })
    }
}

// Integration test example
func TestRepository_CreateUser(t *testing.T) {
    db := setupTestDB(t)
    defer teardownTestDB(t, db)
    
    repo := NewRepository(db)
    user := &User{
        Email: "test@example.com",
        Name:  "Test User",
    }
    
    err := repo.CreateUser(context.Background(), user)
    assert.NoError(t, err)
    assert.NotZero(t, user.UserID)
}
```

### API Testing with OpenAPI Validation

```go
func TestAPICompliance(t *testing.T) {
    // Load OpenAPI specification
    spec, err := loads.Spec("../../openapi.yaml")
    require.NoError(t, err)
    
    // Test each endpoint against specification
    endpoints := []string{
        "/quiz",
        "/plaid/connect",
        "/anomalies/yearly",
        "/trends",
        "/spending/categories",
        "/goal/computed",
        "/habits",
        "/streak/weekly",
        "/spending/status",
        "/savings/weekly",
        "/streak/longest",
        "/spending/total",
    }
    
    for _, endpoint := range endpoints {
        t.Run(endpoint, func(t *testing.T) {
            // Validate endpoint against OpenAPI spec
        })
    }
}
```

## Deployment Configuration

### Docker Compose Structure

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - go-api
    networks:
      - noumi-network

  go-api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgres://user:password@postgres:5432/noumidb
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - noumi-network

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=noumidb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d noumidb"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - noumi-network

  migration:
    build:
      context: .
      dockerfile: Dockerfile.migration
    environment:
      - DATABASE_URL=postgres://user:password@postgres:5432/noumidb
      - SQLITE_PATH=/data/noumi.db
    volumes:
      - ./Back_End/Middleware:/data
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - noumi-network

volumes:
  postgres_data:

networks:
  noumi-network:
    driver: bridge
```

### Environment Configuration

```go
type Config struct {
    Server struct {
        Port         string `env:"PORT" envDefault:"8080"`
        Host         string `env:"HOST" envDefault:"0.0.0.0"`
        ReadTimeout  time.Duration `env:"READ_TIMEOUT" envDefault:"30s"`
        WriteTimeout time.Duration `env:"WRITE_TIMEOUT" envDefault:"30s"`
    }
    
    Database struct {
        URL             string `env:"DATABASE_URL" envDefault:"postgres://localhost/noumidb"`
        MaxOpenConns    int    `env:"DB_MAX_OPEN_CONNS" envDefault:"25"`
        MaxIdleConns    int    `env:"DB_MAX_IDLE_CONNS" envDefault:"5"`
        ConnMaxLifetime time.Duration `env:"DB_CONN_MAX_LIFETIME" envDefault:"5m"`
    }
    
    OpenAI struct {
        APIKey      string `env:"OPENAI_API_KEY"`
        Model       string `env:"OPENAI_MODEL" envDefault:"gpt-4"`
        MaxTokens   int    `env:"OPENAI_MAX_TOKENS" envDefault:"1000"`
        Temperature float32 `env:"OPENAI_TEMPERATURE" envDefault:"0.7"`
    }
    
    Auth struct {
        JWTSecret     string        `env:"JWT_SECRET"`
        TokenExpiry   time.Duration `env:"TOKEN_EXPIRY" envDefault:"24h"`
        RefreshExpiry time.Duration `env:"REFRESH_EXPIRY" envDefault:"168h"`
    }
    
    Logging struct {
        Level  string `env:"LOG_LEVEL" envDefault:"info"`
        Format string `env:"LOG_FORMAT" envDefault:"json"`
    }
}
```

This design provides a comprehensive foundation for migrating the Python FastAPI backend to a modern, scalable Go Gin implementation with full containerization support.