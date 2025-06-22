# 🏦 Noumi AI Financial Planning System

A comprehensive AI-powered financial planning and analysis system with REST API endpoints for weekly plan generation and performance tracking.

## 📁 Project Structure

```
noumi/
├── README.md                           # 📖 This overview file
├── noumi_api.py                        # 🚀 Main REST API server
├── api_examples.py                     # 🧪 API client examples & testing
├── comprehensive_agent_demo.py         # 🔗 Complete agent integration demo
├── requirements_api.txt                # 📦 API dependencies
├── sample_data/                        # 📊 Realistic sample data
│   ├── realistic_transactions.json
│   └── realistic_quiz_responses.json
├── noumi_agents/                       # 🤖 Core AI agents
│   ├── quiz_agent/                     # 👤 User profiling agent
│   ├── transaction_agent/              # 💳 Transaction analysis agent
│   ├── planning_agent/                 # 📋 Financial planning agents
│   │   ├── chain_of_guidance_planner.py  # ⭐ Main planning agent
│   │   └── recap_agent.py               # 📊 Performance analysis agent
│   └── utils/                          # 🔧 Shared utilities
└── docs/                              # 📚 Documentation
    ├── API_USAGE_GUIDE.md            # 🔌 Complete API documentation
    ├── API_IMPLEMENTATION_SUMMARY.md # 📋 Implementation overview
    ├── JSON_FORMAT_REFERENCE.md      # 🗂️ JSON format specifications
    ├── DETAILED_JSON_FORMATS.md      # 📊 Extended format docs
    └── FINAL_CLEANUP_SUMMARY.md      # 🧹 System cleanup summary
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd noumi
pip install -r requirements_api.txt
```

### 2. Start the API Server
```bash
python noumi_api.py
```
Server starts on `http://localhost:5000`

### 3. Test the System
```bash
# Test all API endpoints
python api_examples.py

# Or test agent integration
python comprehensive_agent_demo.py
```

## 🎯 Main Features

### **REST API Endpoints**

#### 📊 **Generate Weekly Plan** - `POST /api/generate-weekly-plan`
- **Input**: User profile + Historical transactions JSON
- **Output**: Weekly financial plan with ML features
- **Key ML Features**: `suggested_savings_amount`, `spending_efficiency_score`

#### 📈 **Generate Weekly Recap** - `POST /api/generate-weekly-recap`
- **Input**: Weekly plan + Actual transactions JSON  
- **Output**: Performance analysis with scores and insights
- **Key ML Features**: `overall_performance_score`, `spending_adherence_rate`

### **AI Agent System**
- **Quiz Agent**: User profiling and preference analysis
- **Plaid Agent**: Transaction analysis and spending patterns
- **Planning Agent**: Weekly financial plan generation with ML features
- **Recap Agent**: Performance analysis and insights generation

## 🧮 **ML Features Extracted**

### Planning Features (Weekly Plan)
```python
ml_features = weekly_plan["ml_features"]
suggested_savings_amount = ml_features["suggested_savings_amount"]  # USD
spending_efficiency_score = ml_features["spending_efficiency_score"]  # 0-100
```

### Performance Features (Weekly Recap)
```python
performance_scores = weekly_recap["performance_scores"]
overall_performance_score = performance_scores["overall_performance_score"]  # 0-100
spending_adherence_rate = weekly_recap["spending_performance"]["spending_adherence_rate"]  # 0-1
```

## 📖 Documentation

### **Primary References**
- **[API_USAGE_GUIDE.md](API_USAGE_GUIDE.md)** - Complete API documentation with examples
- **[API_IMPLEMENTATION_SUMMARY.md](API_IMPLEMENTATION_SUMMARY.md)** - Implementation overview and integration guide

### **Format Specifications**
- **[JSON_FORMAT_REFERENCE.md](JSON_FORMAT_REFERENCE.md)** - Quick JSON format reference
- **[DETAILED_JSON_FORMATS.md](DETAILED_JSON_FORMATS.md)** - Extended format specifications

### **System Information**
- **[FINAL_CLEANUP_SUMMARY.md](FINAL_CLEANUP_SUMMARY.md)** - System cleanup and optimization summary

## 🔧 **Example Usage**

### Python Client
```python
import requests

# Generate weekly plan
response = requests.post('http://localhost:5000/api/generate-weekly-plan', json={
    "user_profile": {
        "user_id": "user_12345",
        "savings_goal": "Emergency fund",
        "monthly_income": 4500.0,
        "risk_tolerance": "moderate",
        "financial_knowledge": "intermediate"
    },
    "transactions": [
        {
            "transaction_id": "txn_001",
            "amount": -127.89,
            "description": "WHOLE FOODS MARKET",
            "category": ["Food and Drink"],
            "date": "2024-06-01"
        }
    ]
})

# Extract ML features
result = response.json()
weekly_plan = result["weekly_plan"]
suggested_savings = weekly_plan["ml_features"]["suggested_savings_amount"]
efficiency_score = weekly_plan["ml_features"]["spending_efficiency_score"]

print(f"Suggested weekly savings: ${suggested_savings}")
print(f"Spending efficiency: {efficiency_score}/100")
```

### cURL Example
```bash
curl -X POST http://localhost:5000/api/generate-weekly-plan \
  -H "Content-Type: application/json" \
  -d '{"user_profile": {"user_id": "user_123", ...}, "transactions": [...]}'
```

## 🏗️ **Architecture**

```
User Input → Quiz Agent → User Preferences
                                      ↓
Transactions → Plaid Agent → Spending Analysis
                                      ↓
User Preferences + Spending Analysis → Planning Agent → Weekly Plan (ML Features)
                                                              ↓
Weekly Plan + Actual Transactions → Recap Agent → Performance Analysis (ML Features)
```

## 🧪 **Testing**

### API Testing
```bash
python api_examples.py
```
- Tests all API endpoints
- Generates sample results
- Saves results to timestamped JSON files

### Agent Integration Testing
```bash
python comprehensive_agent_demo.py
```
- Tests complete agent pipeline
- Shows detailed agent interactions
- Demonstrates ML feature extraction

## 🚀 **Production Deployment**

### Docker (Recommended)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements_api.txt .
RUN pip install -r requirements_api.txt
COPY . .
EXPOSE 5000
CMD ["python", "noumi_api.py"]
```

### Health Monitoring
```bash
curl http://localhost:5000/api/health
```

## 🔌 **Integration**

### For Financial Apps
1. **Weekly Planning**: Send user profile + transaction history → Get weekly plan with ML features
2. **Performance Tracking**: Send weekly plan + actual transactions → Get performance analysis

### For ML Pipelines
Extract key features for model training:
- `suggested_savings_amount` - Target savings prediction
- `spending_efficiency_score` - Optimization score  
- `overall_performance_score` - User performance rating
- `spending_adherence_rate` - Budget compliance rate

## 📊 **Sample Data**

Realistic sample data provided in `sample_data/`:
- **realistic_transactions.json** - 15 diverse transaction examples
- **realistic_quiz_responses.json** - 19 comprehensive user profile fields

## 🎉 **System Status**

✅ **Production Ready**
- Complete REST API with error handling
- Comprehensive documentation  
- ML feature extraction ready
- Client examples provided
- Docker deployment ready

✅ **Fully Tested**  
- All endpoints verified working
- Agent integration confirmed
- ML features extractable
- Sample data provided

## 📞 **Getting Help**

1. **API Issues**: Check [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md)
2. **Integration**: See [API_IMPLEMENTATION_SUMMARY.md](API_IMPLEMENTATION_SUMMARY.md)
3. **JSON Formats**: Reference [JSON_FORMAT_REFERENCE.md](JSON_FORMAT_REFERENCE.md)
4. **Testing**: Run `python api_examples.py`

---

**The Noumi AI Financial Planning System is ready for production use! 🚀**

Integrate into your application using the REST API endpoints or use the agent system directly for advanced financial planning and performance analysis. 