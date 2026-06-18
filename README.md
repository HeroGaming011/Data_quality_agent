# AI Data Quality Agent

A complete Python project featuring a premium **Streamlit** web interface that scans uploaded CSV files for typical data quality issues, automatically detects column attributes (inferred types, completeness, and unique counts), and uses the **OpenRouter API** (model `nex-agi/nex-n2-pro:free`) to generate intelligent suggestions and fully executable Python pandas clean-up scripts.

---

## Team Members

| Name | Roll No | Branch | Role |
|------|----------|--------|------|
| Pragada Harika | 23U41A0547 | CSE |  Team Lead & Documentation|
| Ydesi Chanti Babu | 23U41A0560 | CSE | Data Quality Engine Developer |
| Nanepalli Deepika | 23U41A4430 | CSD | AI/LLM Integration Developer |
| Jyothula Bhargavi | 23U41A0428 | ECE | Testing Engineer and Frontend |

 ### Demo Video
  [click here to view Demo Video](https://www.loom.com/share/8d13d56dada54b599d0c95893d58f9bb)

## Key Features

1. **Inferred Column Attributes**:
   - Analyzes columns to detect data types dynamically (Numeric, Categorical, Boolean, Email, Datetime, or Text/String).
   - Reports unique value counts and completeness percentages per column.
2. **Rule-Based Validation Engine**:
   - Detects duplicate rows.
   - Flags missing or null values in any column (with customized notices for standard columns: `name`, `roll number`/`rooll number`, `Age`, `email`).
   - Identifies mixed data types within the same column.
   - Validates `email` formatting for email-like columns.
   - Flags negative numbers in columns that should only be positive.
   - Identifies outliers in numerical columns using the Interquartile Range (IQR) method.
   - Detects leading or trailing whitespaces in values.
3. **AI-Powered Recommendations**:
   - Sends the validation errors and column attributes summary to OpenRouter.
   - Uses the **`nex-agi/nex-n2-pro:free`** model (outputs structured JSON format).
   - Generates detailed diagnosis, manual clean-up guidelines, and a ready-to-run Python script.
4. **Premium Responsive User Interface**:
   - Streamlit layout with custom HSL/CSS styles, a sidebar upload box, data preview tables, and textareas called **"Detected Errors"** and **"AI Suggestions"**.

---

## Folder Structure

```text
ai_data_quality_agent/
├── .streamlit/
│   └── secrets.toml    # Streamlit secrets configuration (holds API key)
├── app.py              # Main Streamlit application containing UI layout & validation engine
├── llm_helper.py       # API client wrapper for OpenRouter (Nex-AGI)
├── requirements.txt    # Python dependencies list
├── sample_data.csv     # Mock CSV file with typical data errors for testing
├── .env.template       # Environment variables template
└── README.md           # Documentation & instructions
```

---

## Installation & Setup Instructions

### 1. Prerequisites
- **Python 3.8** or higher installed.

### 2. Copy the Files
Ensure all project files are in a folder named `ai_data_quality_agent`.

### 3. Setup Virtual Environment & Install Dependencies
Open a terminal (PowerShell or Command Prompt) and run:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.\venv\Scripts\activate.bat
# On Linux/macOS:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 4. Configure OpenRouter API Key
You can configure your OpenRouter API Key using either of the following two methods:

#### Method A: Streamlit Secrets (Recommended)
1. Create a directory named `.streamlit` in the root folder of the project.
2. Inside `.streamlit`, create a file named `secrets.toml`.
3. Add your OpenRouter API key to the `secrets.toml` file:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-YourActualAPIKeyHere"
   ```

#### Method B: Environment Variable (.env)
1. Create a file named `.env` in the root folder of the project.
2. Add your OpenRouter API key to the `.env` file:
   ```env
   OPENROUTER_API_KEY="sk-or-v1-YourActualAPIKeyHere"
   ```

---

## How to Run the App

With your virtual environment activated, run:
```bash
streamlit run app.py
```

The application will launch and open automatically in your browser:
- **Local URL**: `http://localhost:8501`

---

## Testing with Sample Data

1. Launch the application.
2. Click the file upload box in the sidebar and choose `sample_data.csv` (located in the project folder).
3. The app will:
   - Preview the dataset in an interactive grid.
   - List the column types, completeness, and status in the **Detected Column Attributes** grid.
   - Display duplicate rows, missing names/emails, negative ages, and outliers in the **Detected Errors** textbox.
   - Request suggestions from OpenRouter and print the clean-up plan and Python script in the **AI Suggestions** textbox.
  
### 5. Runnig App Link

  [Click Here to fill Open the Completed App](https://dataqualityagent-dnee7zzsjqjutjtfignsoq.streamlit.app/)


### GitHub Link 
[Click Here to go to GitHub](https://github.com/ydesichantibabu/AI_Data_quality_agent.git)
