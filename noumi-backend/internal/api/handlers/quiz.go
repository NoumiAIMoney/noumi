package handlers

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"

	"noumi-backend/internal/api/middleware"
	"noumi-backend/internal/database/models"
	"noumi-backend/internal/database/repository"
	"noumi-backend/internal/utils/validator"
)

// QuizHandler handles quiz-related HTTP requests
type QuizHandler struct {
	goalRepo  repository.GoalRepository
	validator *validator.Validator
	logger    *logrus.Logger
}

// NewQuizHandler creates a new quiz handler
func NewQuizHandler(goalRepo repository.GoalRepository, logger *logrus.Logger) *QuizHandler {
	return &QuizHandler{
		goalRepo:  goalRepo,
		validator: validator.New(),
		logger:    logger,
	}
}

// SubmitQuiz handles POST /quiz endpoint
// @Summary Submit quiz data to create a financial goal
// @Description Creates a new financial goal based on quiz submission data
// @Tags quiz
// @Accept json
// @Produce json
// @Param quiz body models.QuizSubmission true "Quiz submission data"
// @Success 200 {object} models.GoalResponse "Goal created successfully"
// @Failure 400 {object} middleware.ErrorResponse "Validation error"
// @Failure 401 {object} middleware.ErrorResponse "Authentication error"
// @Failure 500 {object} middleware.ErrorResponse "Internal server error"
// @Security BearerAuth
// @Router /quiz [post]
func (h *QuizHandler) SubmitQuiz(c *gin.Context) {
	requestID := middleware.GetRequestID(c)

	// Get user ID from authentication context
	userID, exists := middleware.GetUserID(c)
	if !exists {
		h.logger.WithField("request_id", requestID).Error("User ID not found in context")
		c.Error(&middleware.AuthenticationError{
			Message: "Authentication required",
			Details: "User ID not found in request context",
		})
		return
	}

	// Parse request body
	var quizSubmission models.QuizSubmission
	if err := c.ShouldBindJSON(&quizSubmission); err != nil {
		h.logger.WithFields(logrus.Fields{
			"request_id": requestID,
			"user_id":    userID,
			"error":      err.Error(),
		}).Warn("Failed to parse quiz submission JSON")

		c.Error(&middleware.ValidationError{
			Message: "Invalid request format",
			Details: "Failed to parse JSON request body",
		})
		return
	}

	// Validate request data
	if err := h.validator.ValidateStruct(&quizSubmission); err != nil {
		h.logger.WithFields(logrus.Fields{
			"request_id": requestID,
			"user_id":    userID,
			"error":      err.Error(),
		}).Warn("Quiz submission validation failed")

		c.Error(err)
		return
	}

	// Convert quiz submission to goal model
	goal := &models.Goal{
		UserID:           userID,
		GoalName:         quizSubmission.GoalName,
		GoalDescription:  quizSubmission.GoalDescription,
		GoalAmount:       quizSubmission.GoalAmount,
		TargetDate:       quizSubmission.TargetDate,
		NetMonthlyIncome: &quizSubmission.NetMonthlyIncome,
		CreatedAt:        time.Now().UTC(),
	}

	// Validate target date is in the future
	if goal.TargetDate.Before(time.Now()) {
		h.logger.WithFields(logrus.Fields{
			"request_id":  requestID,
			"user_id":     userID,
			"target_date": goal.TargetDate,
		}).Warn("Target date is in the past")

		c.Error(&middleware.ValidationError{
			Message: "Invalid target date",
			Details: "Target date must be in the future",
		})
		return
	}

	// Save goal to database
	if err := h.goalRepo.Create(c.Request.Context(), goal); err != nil {
		h.logger.WithFields(logrus.Fields{
			"request_id": requestID,
			"user_id":    userID,
			"error":      err.Error(),
		}).Error("Failed to create goal in database")

		c.Error(&middleware.DatabaseError{
			Message: "Failed to save goal",
			Details: "Database operation failed",
		})
		return
	}

	h.logger.WithFields(logrus.Fields{
		"request_id": requestID,
		"user_id":    userID,
		"goal_id":    goal.GoalID,
		"goal_name":  goal.GoalName,
	}).Info("Quiz submitted successfully, goal created")

	// Return success response
	c.JSON(http.StatusOK, gin.H{
		"message": "Quiz submitted successfully",
		"goal":    goal.ToResponse(),
	})
}
