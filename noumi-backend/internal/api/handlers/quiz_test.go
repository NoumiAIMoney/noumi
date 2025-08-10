package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	"noumi-backend/internal/api/middleware"
	"noumi-backend/internal/database/models"
)

// MockGoalRepository is a mock implementation of GoalRepository
type MockGoalRepository struct {
	mock.Mock
}

func (m *MockGoalRepository) Create(ctx context.Context, goal *models.Goal) error {
	args := m.Called(ctx, goal)
	// Set a mock goal ID for successful creation
	if args.Error(0) == nil {
		goal.GoalID = 1
		goal.CreatedAt = time.Now().UTC()
	}
	return args.Error(0)
}

func (m *MockGoalRepository) GetByID(ctx context.Context, goalID int) (*models.Goal, error) {
	args := m.Called(ctx, goalID)
	return args.Get(0).(*models.Goal), args.Error(1)
}

func (m *MockGoalRepository) GetByUserID(ctx context.Context, userID int) ([]*models.Goal, error) {
	args := m.Called(ctx, userID)
	return args.Get(0).([]*models.Goal), args.Error(1)
}

func (m *MockGoalRepository) GetLatestByUserID(ctx context.Context, userID int) (*models.Goal, error) {
	args := m.Called(ctx, userID)
	return args.Get(0).(*models.Goal), args.Error(1)
}

func (m *MockGoalRepository) Update(ctx context.Context, goal *models.Goal) error {
	args := m.Called(ctx, goal)
	return args.Error(0)
}

func (m *MockGoalRepository) Delete(ctx context.Context, goalID int) error {
	args := m.Called(ctx, goalID)
	return args.Error(0)
}

func TestQuizHandler_SubmitQuiz(t *testing.T) {
	// Set Gin to test mode
	gin.SetMode(gin.TestMode)

	tests := []struct {
		name           string
		userID         int
		requestBody    models.QuizSubmission
		mockError      error
		expectedStatus int
		expectedBody   string
	}{
		{
			name:   "successful quiz submission",
			userID: 1,
			requestBody: models.QuizSubmission{
				GoalName:         "Emergency Fund",
				GoalDescription:  "Build an emergency fund for unexpected expenses",
				GoalAmount:       10000.00,
				TargetDate:       time.Now().AddDate(1, 0, 0), // 1 year from now
				NetMonthlyIncome: 5000.00,
			},
			mockError:      nil,
			expectedStatus: http.StatusOK,
			expectedBody:   "Quiz submitted successfully",
		},
		{
			name:   "validation error - missing goal name",
			userID: 1,
			requestBody: models.QuizSubmission{
				GoalName:         "", // Missing required field
				GoalDescription:  "Build an emergency fund for unexpected expenses",
				GoalAmount:       10000.00,
				TargetDate:       time.Now().AddDate(1, 0, 0),
				NetMonthlyIncome: 5000.00,
			},
			mockError:      nil,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   "goal_name is required",
		},
		{
			name:   "validation error - invalid goal amount",
			userID: 1,
			requestBody: models.QuizSubmission{
				GoalName:         "Emergency Fund",
				GoalDescription:  "Build an emergency fund for unexpected expenses",
				GoalAmount:       -1000.00, // Invalid negative amount
				TargetDate:       time.Now().AddDate(1, 0, 0),
				NetMonthlyIncome: 5000.00,
			},
			mockError:      nil,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   "goal_amount must be greater than 0",
		},
		{
			name:   "validation error - target date in past",
			userID: 1,
			requestBody: models.QuizSubmission{
				GoalName:         "Emergency Fund",
				GoalDescription:  "Build an emergency fund for unexpected expenses",
				GoalAmount:       10000.00,
				TargetDate:       time.Now().AddDate(-1, 0, 0), // Past date
				NetMonthlyIncome: 5000.00,
			},
			mockError:      nil,
			expectedStatus: http.StatusBadRequest,
			expectedBody:   "Target date must be in the future",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create mock repository
			mockRepo := new(MockGoalRepository)
			if tt.mockError != nil || (tt.expectedStatus == http.StatusOK) {
				mockRepo.On("Create", mock.Anything, mock.AnythingOfType("*models.Goal")).Return(tt.mockError)
			}

			// Create handler
			logger := logrus.New()
			logger.SetLevel(logrus.ErrorLevel) // Reduce log noise in tests
			handler := NewQuizHandler(mockRepo, logger)

			// Create request body
			requestBody, err := json.Marshal(tt.requestBody)
			assert.NoError(t, err)

			// Create HTTP request
			req, err := http.NewRequest(http.MethodPost, "/quiz", bytes.NewBuffer(requestBody))
			assert.NoError(t, err)
			req.Header.Set("Content-Type", "application/json")

			// Create response recorder
			w := httptest.NewRecorder()

			// Create Gin context with error handling middleware
			c, router := gin.CreateTestContext(w)
			router.Use(middleware.ErrorHandlerMiddleware(logger))
			c.Request = req

			// Set user ID in context (simulate authentication middleware)
			c.Set(middleware.UserIDKey, tt.userID)
			c.Set(middleware.RequestIDKey, "test-request-id")

			// Call handler
			handler.SubmitQuiz(c)

			// Process any errors through middleware
			if len(c.Errors) > 0 {
				middleware.ErrorHandlerMiddleware(logger)(c)
			}

			// Check status code
			assert.Equal(t, tt.expectedStatus, w.Code)

			// Check response body contains expected content
			responseBody := w.Body.String()
			assert.Contains(t, responseBody, tt.expectedBody)

			// Verify mock expectations
			mockRepo.AssertExpectations(t)
		})
	}
}

func TestQuizHandler_SubmitQuiz_NoAuth(t *testing.T) {
	// Set Gin to test mode
	gin.SetMode(gin.TestMode)

	// Create mock repository
	mockRepo := new(MockGoalRepository)

	// Create handler
	logger := logrus.New()
	logger.SetLevel(logrus.ErrorLevel)
	handler := NewQuizHandler(mockRepo, logger)

	// Create request body
	requestBody := models.QuizSubmission{
		GoalName:         "Emergency Fund",
		GoalDescription:  "Build an emergency fund for unexpected expenses",
		GoalAmount:       10000.00,
		TargetDate:       time.Now().AddDate(1, 0, 0),
		NetMonthlyIncome: 5000.00,
	}

	body, err := json.Marshal(requestBody)
	assert.NoError(t, err)

	// Create HTTP request
	req, err := http.NewRequest(http.MethodPost, "/quiz", bytes.NewBuffer(body))
	assert.NoError(t, err)
	req.Header.Set("Content-Type", "application/json")

	// Create response recorder
	w := httptest.NewRecorder()

	// Create Gin context without user ID (no authentication)
	c, router := gin.CreateTestContext(w)
	router.Use(middleware.ErrorHandlerMiddleware(logger))
	c.Request = req
	c.Set(middleware.RequestIDKey, "test-request-id")

	// Call handler
	handler.SubmitQuiz(c)

	// Process any errors through middleware
	if len(c.Errors) > 0 {
		middleware.ErrorHandlerMiddleware(logger)(c)
	}

	// Should have an authentication error in the context
	assert.True(t, len(c.Errors) > 0)
	assert.Contains(t, c.Errors[0].Error(), "Authentication required")
}
