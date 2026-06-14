import os
import json
import streamlit as st
from dotenv import load_dotenv
import openai

# Load environment variables, overriding any pre-existing environment variables
project_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(project_dir, '.env')
load_dotenv(dotenv_path=env_path, override=True)

def get_openai_suggestions(errors_text: str, data_preview: str, attributes_summary: str = "") -> str:
    """
    Sends the validation error reports, column attributes summary, and a preview of the data 
    to OpenRouter using the nex-agi/nex-n2-pro:free model.
    """
    # 1. Retrieve the OpenRouter API Key from Streamlit Secrets or Environment Variables
    api_key = None
    try:
        if "OPENROUTER_API_KEY" in st.secrets:
            api_key = st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        # st.secrets raises an exception if not running in Streamlit environment
        pass

    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY")
    
    # Check if the API key is empty
    if not api_key or api_key.strip() == "":
        return (
            "⚠️ OpenRouter API Key not configured!\n\n"
            "Please configure your OpenRouter API Key using one of these methods:\n"
            "1. **Streamlit Secrets** (Recommended for Streamlit):\n"
            "   Create a `.streamlit/secrets.toml` file and add:\n"
            "   `OPENROUTER_API_KEY = \"your_openrouter_api_key\"`\n"
            "2. **Environment Variable**:\n"
            "   Create a `.env` file in the project folder containing:\n"
            "   `OPENROUTER_API_KEY=\"your_openrouter_api_key\"`"
        )

    # Clean the API key from spaces and potential quotes
    api_key = api_key.strip().strip('"').strip("'")

    if api_key in ["your_openrouter_api_key_here", "your_api_key_here"]:
        return "⚠️ Please replace the placeholder API key in your configuration with your actual OpenRouter API key."

    # Debug print in terminal
    print(f"[DEBUG] OpenRouter Key detected starting with: {api_key[:12]}...")
    print(f"[DEBUG] Endpoint: https://openrouter.ai/api/v1 | Model: nex-agi/nex-n2-pro:free")

    try:
        # Initialize client with OpenRouter base URL and default headers
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={"HTTP-Referer": "https://streamlit.io/"}
        )
        
        prompt = f"""
You are an expert AI Data Quality Engineer.
A user has uploaded a CSV file, and we have scanned it for data quality issues and anomalies.

### CSV Dataset Preview (First few rows):
```csv
{data_preview}
```
"""

        if attributes_summary:
            prompt += f"""
### Inferred Dataset Column Attributes:
```text
{attributes_summary}
```
"""

        prompt += f"""
### Detected Data Quality Errors/Anomalies:
{errors_text}

Analyze these errors and provide suggestions.
You must respond with a JSON object containing these exact keys:
1. "diagnosis": An explanation of why these anomalies occurred and any patterns you notice.
2. "suggestions": Step-by-step guidance on how to fix these anomalies manually or programmatically.
3. "cleanup_script": A complete, ready-to-run Python script using Pandas that reads a dataset (e.g. 'dataset.csv'), cleans up these exact errors, and saves the cleaned dataset as 'cleaned_dataset.csv'. Ensure the script uses the correct column names as shown in the preview.

JSON Output Format:
{{
    "diagnosis": "Explanation here",
    "suggestions": "Suggestions here",
    "cleanup_script": "import pandas as pd\\n..."
}}
"""
        
        # Call the chat completions model with json_object format
        response = client.chat.completions.create(
            model="nex-agi/nex-n2-pro:free",
            messages=[
                {"role": "system", "content": "You are a professional Data Quality Engineer. You must output JSON."},
                {"role": "user", "content": prompt}
            ],
            extra_body={"response_format": {"type": "json_object"}}
        )
        
        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content
            # Parse the JSON response and format it nicely for the text area output
            try:
                data = json.loads(content)
                diagnosis = data.get("diagnosis", "")
                suggestions = data.get("suggestions", "")
                script = data.get("cleanup_script", "")
                
                formatted_response = f"""### 🔍 Diagnosis Summary
{diagnosis}

### 📋 Actionable Suggestions
{suggestions}

### 🐍 Python Cleanup Script
```python
{script}
```"""
                return formatted_response
            except json.JSONDecodeError:
                # If JSON parsing fails, fallback to raw text output
                return content
        else:
            return "❌ OpenRouter returned an empty response."
            
    except openai.OpenAIError as api_err:
        return (
            f"❌ OpenRouter API Error: {str(api_err)}\n\n"
            "Troubleshooting Steps:\n"
            "1. Verify that your API key in the secrets or environment is correct.\n"
            "2. Ensure you have network connectivity.\n"
            "3. Check if your API usage has exceeded quota limits."
        )
    except Exception as e:
        return f"❌ An unexpected error occurred while calling the OpenRouter API: {str(e)}"
