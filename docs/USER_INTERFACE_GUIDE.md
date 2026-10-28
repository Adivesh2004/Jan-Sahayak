# User-Friendly Interface Guide

## Overview

The new user interface provides a simplified, intuitive way to interact with the Zynd Civic Assistant system through 4 main options:

1. **💰 Check Benefits** - Discover all government benefits you qualify for
2. **✅ Verify Eligibility** - Check if you qualify for a specific scheme
3. **📜 Explain Policy** - Understand any government policy in simple terms
4. **📝 Help Fill Application** - Get step-by-step guidance to apply

## Running the Interface

### Quick Start

```powershell
# From the project root
streamlit run src/user_interface.py
```

The interface will open in your browser at `http://localhost:8501`

### Using the Old Interface (CLI or Original Streamlit)

```powershell
# Command-line interface
python src/main.py

# Original chat-based Streamlit
streamlit run src/streamlit_app.py
```

## How It Works

### 1. Select an Option

On the home page, click one of the 4 main option buttons based on what you need.

### 2. Answer Questions

Each option will present relevant questions:

- **Check Benefits** asks about: age, income, location, employment, family size, education, category
- **Verify Eligibility** asks about: scheme name + your profile information
- **Explain Policy** asks: which policy and what aspect to explain
- **Help Application** asks: scheme name, documents available, application stage

All questions include:
- Clear labels and descriptions
- Help text explaining why the question matters
- Input validation with helpful error messages
- Required vs optional field indicators

### 3. Get Results

After submitting, the system:
1. Validates your inputs
2. Builds a comprehensive query from your answers
3. Routes to the appropriate agent(s)
4. Displays personalized, actionable results

### 4. Custom Queries

Don't fit into one of the 4 options? Use the free-form text box at the bottom of the home page to ask anything directly.

## Features

### Input Validation

- **Age**: Must be 0-120
- **Income**: Positive numbers, formatted correctly
- **Location**: Valid state/region names
- **Scheme/Policy**: Minimum 3 characters
- **Family Size**: At least 1 member

### Context Sharing

The system maintains your profile across all agent interactions:
- Once you provide your age, income, etc., agents use this context
- No need to repeat information
- More accurate, personalized responses

### Synchronous Operation

Each agent waits for previous processing to complete, ensuring:
- Coherent responses
- Proper context flow
- No race conditions

### Progress Indicators

Visual feedback during processing:
- 🧠 Routing your request
- 📜 Analyzing policy documents
- ✅ Checking eligibility criteria
- 💰 Searching for benefits
- 📢 Preparing guidance

## Example Workflows

### Check Benefits Workflow
1. Click "💰 Check Benefits"
2. Enter: Age=35, Income=200000, Location=Maharashtra, Employment=Farmer, Family=4
3. System discovers PM-KISAN, PMFBY, Ayushman Bharat, etc.
4. View detailed results with eligibility reasoning

### Verify Eligibility Workflow
1. Click "✅ Verify Eligibility"
2. Enter scheme: "Ayushman Bharat"
3. Provide profile information
4. Get clear YES/NO with reasoning and next steps

### Explain Policy Workflow
1. Click "📜 Explain Policy"
2. Enter policy: "PM-KISAN"
3. Select aspect: "Who is eligible?"
4. Read simple explanation with examples

### Help Application Workflow
1. Click "📝 Help Fill Application"
2. Enter scheme: "PM-SVANidhi"
3. Select documents you have
4. Choose stage: "Just starting"
5. Get step-by-step guidance

## Architecture

### New Files Created

- `src/user_interface.py` - Main Streamlit interface
- `src/question_config.py` - Question definitions for each option
- `src/validators.py` - Input validation utilities

### Modified Files

- `src/state.py` - Added user_profile, selected_option, collected_answers
- `src/graph.py` - Enhanced nodes to use user profile and support direct routing

### State Flow

```
User selects option → Answers questions → Validation →
Build query from answers → Set user_profile in state →
Route to agent (bypass orchestrator if intent known) →
Agent uses profile for context → Generate response → Display
```

## Troubleshooting

### "Module not found" errors
Ensure you're in the project root and virtual environment is activated:
```powershell
cd c:\Users\bhara\Desktop\Projects\zynd-protocals-application
.\venv\Scripts\activate
```

### Port already in use
Streamlit default port 8501 is busy:
```powershell
streamlit run src/user_interface.py --server.port 8502
```

### Validation errors
- Check that inputs match the expected format
- Age and income must be numbers
- Required fields cannot be empty

### No response generated
- Check logs in `logs/` directory
- Verify agents are functioning: `python src/main.py`
- Ensure LLM API keys are set in `.env`

## Next Steps

1. **Test all 4 options** with different inputs
2. **Try edge cases** (very high income, age=0, etc.)
3. **Test custom queries** outside the 4 main options
4. **Verify agent responses** are accurate and helpful
5. **Provide feedback** on question clarity and UX

## Benefits Over Old Interface

| Old Interface | New Interface |
|---------------|---------------|
| Free-form text only | Guided questions + free-form |
| No input validation | Comprehensive validation |
| User must know what to ask | Clear 4-option menu |
| No context preservation | User profile shared across agents |
| Text-based feedback | Visual progress indicators |
| Generic responses | Personalized based on profile |
