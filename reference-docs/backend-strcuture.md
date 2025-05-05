# Financial Advisor App - Backend Structure Documentation

## Overview

This document outlines the backend architecture, components, and data flow for the Financial Advisor application. The backend is built with Python, leveraging LangChain for AI orchestration and integration with Groq models to provide personalized portfolio diversification recommendations.

## Directory Structure

```
financial_advisor/
├── app.py                    # Main Streamlit application entry point
├── backend/
│   ├── __init__.py
│   ├── config.py             # Configuration settings and constants
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_profile.py   # Data models for user financial information
│   │   └── portfolio.py      # Data models for portfolio recommendations
│   ├── services/
│   │   ├── __init__.py
│   │   ├── financial_engine.py   # Financial calculations and processing
│   │   ├── ai_service.py         # LangChain and Groq integration
│   │   └── recommendation.py     # Portfolio recommendation generator
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py     # Input validation helpers
│   │   ├── calculators.py    # Financial math utilities
│   │   └── formatters.py     # Data formatting utilities
│   └── prompts/
│       ├── __init__.py
│       ├── system_prompts.py # AI system instructions
│       └── templates.py      # Dynamic prompt templates
├── tests/
│   ├── __init__.py
│   ├── test_financial_engine.py
│   ├── test_ai_service.py
│   └── test_validators.py
└── requirements.txt         # Project dependencies
```

## Core Components

### 1. Data Models

#### UserProfile Model
- Represents the user's financial situation
- Properties include:
  - Income details (salary, additional income)
  - Expense information (fixed, variable)
  - Debt obligations (loans, interest rates)
  - Current assets (savings, investments)
  - Risk profile (tolerance level, age, time horizon)
  - Financial goals (objectives, timeframes)

#### Portfolio Model
- Represents the recommended portfolio allocation
- Properties include:
  - Asset class allocations (percentages)
  - Sector distributions
  - Geographic allocations
  - Risk metrics
  - Expected returns
  - Recommendation rationales

### 2. Service Layer

#### Financial Engine
- **Purpose**: Core financial calculations and analysis
- **Key Functions**:
  - `calculate_investment_capacity(user_profile)`: Determines how much a user can invest
  - `analyze_debt_situation(user_profile)`: Evaluates debt-to-income ratio and prioritization
  - `determine_risk_profile(user_inputs)`: Maps user responses to risk tolerance level
  - `calculate_savings_rate(income, expenses)`: Computes current savings rate
  - `validate_financial_health(user_profile)`: Checks basic financial health indicators

#### AI Service
- **Purpose**: Integration with Groq AI models via LangChain
- **Key Functions**:
  - `initialize_llm()`: Sets up connection to Groq API
  - `create_chain()`: Configures LangChain processing pipeline
  - `generate_allocation_advice(user_profile)`: Produces investment allocation recommendations
  - `generate_explanation(allocation, user_profile)`: Creates natural language explanation of recommendations
  - `get_next_steps(portfolio, user_profile)`: Recommends implementation steps

#### Recommendation Service
- **Purpose**: Transforms raw AI outputs into structured portfolio recommendations
- **Key Functions**:
  - `create_portfolio_recommendation(user_profile, ai_response)`: Builds structured portfolio object
  - `adjust_for_constraints(portfolio)`: Ensures allocations meet minimum requirements
  - `calculate_expected_returns(portfolio)`: Estimates potential returns based on historical data
  - `format_for_display(portfolio)`: Prepares data for visualization

### 3. Utilities

#### Validators
- Input validation for all user-provided data
- Range checks for financial values
- Logical consistency validation

#### Calculators
- Financial ratio calculations
- Compound interest projections
- Risk/return models
- Tax efficiency calculations

#### Formatters
- Currency formatting functions
- Percentage formatting
- Data structure conversions
- Visualization data preparation

### 4. Prompt Engineering

#### System Prompts
- Core instruction sets for the AI model
- Financial expertise context
- Response format specifications

#### Templates
- Dynamic prompt templates that incorporate user data
- Specialized prompts for different financial scenarios
- Follow-up question generators

## Data Flow

1. **User Input Collection**
   - Streamlit frontend collects financial information
   - Data is validated and normalized
   - User profile object is created

2. **Financial Analysis**
   - Financial Engine processes user profile
   - Calculates key financial metrics
   - Determines investment capacity

3. **AI Processing**
   - User profile and financial metrics sent to AI Service
   - LangChain formats data for Groq model
   - AI generates allocation recommendations and explanations

4. **Recommendation Synthesis**
   - Recommendation Service structures AI output
   - Validates recommendations against financial principles
   - Applies any necessary adjustments or constraints

5. **Response Preparation**
   - Results formatted for visualization
   - Explanation text processed for readability
   - Next steps guidance generated

6. **Display to User**
   - Structured data returned to Streamlit frontend
   - Visualizations rendered
   - Text explanations formatted and displayed

## Integration Points

### LangChain Integration
- Uses LangChain framework to create structured interaction with Groq models
- Implements chains for different recommendation scenarios
- Manages context and memory for follow-up interactions

### Groq API Integration
- Connection configured in config.py
- API key managed via environment variables
- Model selection based on performance requirements
- Error handling and retry logic

## Error Handling Strategy

- Graceful degradation if AI service is unavailable
- Fallback to rule-based recommendations when appropriate
- Comprehensive input validation to prevent processing errors
- Clear user messaging for any system limitations

## Performance Considerations

- Caching of financial calculations where appropriate
- Optimization of AI prompt design for faster responses
- Asynchronous processing for long-running operations
- Resource usage monitoring for Groq API calls

## Security Implementation

- No persistent storage of user financial data
- In-memory processing only
- Secure API communication
- Input sanitization to prevent injection

## Testing Approach

- Unit tests for all financial calculations
- Integration tests for AI service interactions
- Validation of recommendation quality against financial principles
- Performance testing for response times

This backend structure documentation provides a comprehensive blueprint for implementing the server-side logic of the Financial Advisor application, ensuring a robust foundation for generating high-quality portfolio diversification recommendations.