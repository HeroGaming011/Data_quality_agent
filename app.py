import re
import os
import pandas as pd
import streamlit as st
from llm_helper import get_openai_suggestions

# Set page config for a premium look
st.set_page_config(
    page_title="AI Data Quality Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium typography and layout styling
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Apply modern font globally */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}

/* Beautiful gradient header card */
.header-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #3b82f6 100%);
    color: white;
    padding: 2.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px -10px rgba(15, 23, 42, 0.3);
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.header-card h1 {
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    margin-bottom: 0.5rem !important;
    color: white !important;
    background: linear-gradient(to right, #ffffff, #93c5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header-card p {
    font-size: 1.1rem !important;
    font-weight: 300 !important;
    color: #cbd5e1 !important;
    max-width: 800px;
    margin: 0 auto !important;
}

/* Card titles */
.section-title {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    margin-bottom: 0.75rem !important;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 0.25rem;
    display: inline-block;
}

/* Style textareas to look modern and readable */
.stTextArea textarea {
    font-family: 'Consolas', 'Courier New', monospace !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
    background-color: #f8fafc !important;
    color: #0f172a !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


def detect_dataset_attributes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes any DataFrame and infers metadata and attributes of all columns.
    Returns a Summary DataFrame.
    """
    summary_data = []
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    for col in df.columns:
        col_series = df[col]
        total_count = len(col_series)
        null_count = col_series.isna().sum()
        null_pct = (null_count / total_count) * 100 if total_count > 0 else 0
        unique_count = col_series.nunique()
        
        # Inferred Type identification
        if pd.api.types.is_numeric_dtype(col_series):
            if unique_count <= 2 and col_series.dropna().isin([0, 1, 0.0, 1.0]).all():
                inferred_type = "Boolean (0/1)"
            elif pd.api.types.is_integer_dtype(col_series) or (col_series.dropna() % 1 == 0).all():
                inferred_type = "Numeric (Integer)"
            else:
                inferred_type = "Numeric (Float)"
        elif pd.api.types.is_bool_dtype(col_series):
            inferred_type = "Boolean"
        else:
            # Check if Date/Time
            try:
                test_vals = col_series.dropna().head(10).astype(str)
                if not test_vals.empty:
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        pd.to_datetime(test_vals, errors='raise')
                    inferred_type = "Datetime"
                else:
                    inferred_type = "Text/String"
            except (ValueError, TypeError):
                # Check if Email
                non_null_vals = col_series.dropna().astype(str).str.strip()
                if not non_null_vals.empty:
                    email_matches = non_null_vals.str.match(email_regex).sum()
                    if email_matches / len(non_null_vals) >= 0.5:
                        inferred_type = "Email Address"
                    elif unique_count / len(non_null_vals) <= 0.3 or unique_count <= 10:
                        inferred_type = "Categorical"
                    else:
                        inferred_type = "Text/String"
                else:
                    inferred_type = "Empty Column"
        
        # Count anomalies for this column
        column_anomalies = []
        if null_count > 0:
            column_anomalies.append(f"{null_count} nulls")
            
        # Mixed types check
        non_null_vals = col_series.dropna()
        if not non_null_vals.empty:
            types = non_null_vals.map(type).unique()
            if len(types) > 1:
                type_names = [t.__name__ for t in types]
                column_anomalies.append(f"Mixed types ({', '.join(type_names)})")
        
        # Email format issues
        if inferred_type == "Email Address" or "email" in str(col).lower() or "mail" in str(col).lower():
            invalid_emails = 0
            for val in col_series.dropna():
                if not re.match(email_regex, str(val).strip()):
                    invalid_emails += 1
            if invalid_emails > 0:
                column_anomalies.append(f"{invalid_emails} invalid emails")
                
        # Numeric checks
        if pd.api.types.is_numeric_dtype(col_series):
            numeric_vals = col_series.dropna()
            # Age bounds check [0, 100]
            if str(col).lower().strip() == 'age':
                out_of_bounds = numeric_vals[(numeric_vals < 0) | (numeric_vals > 100)].count()
                if out_of_bounds > 0:
                    column_anomalies.append(f"{out_of_bounds} values out of [0, 100] limit")
            else:
                positive_keywords = ['count', 'score', 'total', 'price', 'salary', 'quantity', 'amount', 'id', 'roll', 'rooll']
                if any(kw in str(col).lower() for kw in positive_keywords):
                    neg_count = (numeric_vals < 0).sum()
                    if neg_count > 0:
                        column_anomalies.append(f"{neg_count} negative values")
                        
                # Outlier detection
                if len(numeric_vals) >= 3:
                    q1 = numeric_vals.quantile(0.25)
                    q3 = numeric_vals.quantile(0.75)
                    iqr = q3 - q1
                    if iqr > 0:
                        lower_bound = q1 - 1.5 * iqr
                        upper_bound = q3 + 1.5 * iqr
                        outliers = numeric_vals[(numeric_vals < lower_bound) | (numeric_vals > upper_bound)].count()
                        if outliers > 0:
                            column_anomalies.append(f"{outliers} outliers")
                            
        # Whitespace checking
        if not pd.api.types.is_numeric_dtype(col_series) and inferred_type not in ["Empty Column", "Boolean"]:
            whitespace_count = sum(1 for val in col_series.dropna() if str(val) != str(val).strip())
            if whitespace_count > 0:
                column_anomalies.append(f"{whitespace_count} values with outer whitespaces")

        status = "✅ Clean" if not column_anomalies else "⚠️ " + ", ".join(column_anomalies)
        
        summary_data.append({
            "Column Name": col,
            "Inferred Type": inferred_type,
            "Completeness (%)": f"{100 - null_pct:.1f}%",
            "Unique Values": unique_count,
            "Quality Status": status
        })
        
    return pd.DataFrame(summary_data)


def validate_csv(file_path: str):
    """
    Validates any uploaded CSV file dynamically.
    Checks for duplicates, nulls, mixed types, outliers, formatting.
    """
    try:
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding='latin-1')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='cp1252')
    except pd.errors.EmptyDataError:
        return None, "Error: The uploaded CSV file is empty.", ""
    except pd.errors.ParserError:
        return None, "Error: Could not parse CSV. Please ensure it is a valid comma-separated values file.", ""
    except Exception as e:
        return None, f"Error reading CSV file: {str(e)}", ""

    if df.empty:
        return df, "Error: The CSV contains headers but has no data rows.", ""

    errors = []

    # 1. Check for Duplicate Rows
    duplicates = df.duplicated()
    if duplicates.any():
        dup_rows = df[duplicates].index + 1
        errors.append(f"⚠️ Duplicate rows found at: Row(s) {', '.join(map(str, dup_rows))}")

    # Regex patterns
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    # Normalization of headers for identifying standard columns
    normalized_cols = {str(col).strip().lower(): col for col in df.columns}
    name_col = normalized_cols.get('name')
    roll_col = normalized_cols.get('rooll number') or normalized_cols.get('roll number')
    age_col = normalized_cols.get('age')
    email_col = normalized_cols.get('email')

    # Iterate through columns to perform checks
    for col in df.columns:
        col_series = df[col]
        col_lower = str(col).strip().lower()
        
        # A. Missing/Null values check
        null_indices = col_series[col_series.isna()].index + 1
        if not null_indices.empty:
            if col == name_col:
                errors.append(f"• Row(s) {', '.join(map(str, null_indices))}: Missing name")
            elif col == roll_col:
                errors.append(f"• Row(s) {', '.join(map(str, null_indices))}: Missing roll number")
            elif col == age_col:
                errors.append(f"• Row(s) {', '.join(map(str, null_indices))}: Missing Age")
            elif col == email_col:
                errors.append(f"• Row(s) {', '.join(map(str, null_indices))}: Missing email")
            else:
                errors.append(f"• Column '{col}': Missing values at Row(s) {', '.join(map(str, null_indices))}")

        # B. Mixed types check
        non_null_vals = col_series.dropna()
        if not non_null_vals.empty:
            types = non_null_vals.map(type).unique()
            if len(types) > 1:
                type_names = [t.__name__ for t in types]
                errors.append(f"• Column '{col}': Mixed data types found ({', '.join(type_names)})")

        # C. Age / Numerical checks
        if pd.api.types.is_numeric_dtype(col_series):
            numeric_vals = col_series.dropna()
            if not numeric_vals.empty:
                if col == age_col:
                    out_of_bounds = numeric_vals[(numeric_vals < 0) | (numeric_vals > 100)]
                    if not out_of_bounds.empty:
                        for idx, val in out_of_bounds.items():
                            errors.append(f"• Row {idx + 1}: Age is {val} (must be between 0 and 100)")
                else:
                    positive_keywords = ['count', 'score', 'total', 'price', 'salary', 'quantity', 'amount', 'id', 'roll', 'rooll']
                    if any(kw in col_lower for kw in positive_keywords):
                        neg_indices = numeric_vals[numeric_vals < 0].index + 1
                        if not neg_indices.empty:
                            errors.append(f"• Column '{col}': Negative value(s) found at Row(s) {', '.join(map(str, neg_indices))} (expected non-negative)")

                    # IQR Outlier check
                    if len(numeric_vals) >= 3:
                        q1 = numeric_vals.quantile(0.25)
                        q3 = numeric_vals.quantile(0.75)
                        iqr = q3 - q1
                        if iqr > 0:
                            lower_bound = q1 - 1.5 * iqr
                            upper_bound = q3 + 1.5 * iqr
                            outliers = numeric_vals[(numeric_vals < lower_bound) | (numeric_vals > upper_bound)]
                            if not outliers.empty:
                                outlier_details = []
                                for idx, val in outliers.items():
                                    outlier_details.append(f"Row {idx + 1} (value: {val})")
                                errors.append(f"• Column '{col}': Statistical outlier(s) detected: {', '.join(outlier_details)}")
        else:
            if col == age_col:
                for idx, val in col_series.items():
                    if pd.notna(val):
                        try:
                            val_num = float(val)
                            if val_num < 0 or val_num > 100:
                                errors.append(f"• Row {idx + 1}: Age is {val_num} (must be between 0 and 100)")
                        except ValueError:
                            errors.append(f"• Row {idx + 1}: Age '{val}' is not a valid number")

        # D. Email Format Check
        is_email_col = False
        if col == email_col:
            is_email_col = True
        elif "email" in col_lower or "mail" in col_lower:
            is_email_col = True
        elif not non_null_vals.empty and pd.api.types.is_string_dtype(col_series):
            email_like_count = non_null_vals.astype(str).str.contains('@').sum()
            if email_like_count / len(non_null_vals) >= 0.5:
                is_email_col = True

        if is_email_col:
            for idx, val in col_series.items():
                if pd.notna(val) and str(val).strip() != "":
                    val_str = str(val).strip()
                    if not re.match(email_regex, val_str):
                        if col == email_col:
                            errors.append(f"• Row {idx + 1}: Invalid email format '{val_str}'")
                        else:
                            errors.append(f"• Column '{col}': Invalid email format '{val_str}' at Row {idx + 1}")

        # E. Formatting issues (leading/trailing whitespace)
        if not pd.api.types.is_numeric_dtype(col_series):
            for idx, val in col_series.items():
                if pd.notna(val) and str(val) != str(val).strip():
                    errors.append(f"• Column '{col}', Row {idx + 1}: Value contains leading/trailing whitespaces ('{val}')")

    if not errors:
        errors_output = "✅ No data quality issues or anomalies detected! The dataset is clean."
    else:
        errors_output = f"⚠️ Detected {len(errors)} data quality warning(s)/anomaly(ies) in dataset:\n\n" + "\n".join(errors)

    preview_df = df.head(5)
    preview_text = preview_df.to_csv(index=False)

    return df, errors_output, preview_text


# --- STREAMLIT UI LAYOUT ---

# Header Section
st.markdown(
    """
    <div class="header-card">
        <h1>🔍 AI Data Quality Agent</h1>
        <p>
            Upload any CSV dataset to scan for data quality issues and anomalies. 
            Our automated rule engine dynamically checks for missing values, duplicates, mixed types, email formats, and outliers, 
            while <b>OpenRouter (Nex-AGI)</b> diagnoses patterns and writes custom Python cleanup scripts!
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### 📄 Upload CSV")
    uploaded_file = st.file_uploader(
        "Choose a CSV File",
        type=["csv"],
        help="Upload any dataset to trigger validation and recommendations."
    )
    
    st.markdown("---")
    st.markdown("### 🔍 Rule Engine Specification")
    st.markdown(
        """
        The agent dynamically scans any dataset:
        1. **Universal Checks**:
           - Duplicate rows.
           - Null or missing values in any column.
           - Mixed data types.
        2. **Text Formatting**:
           - Outer whitespace warnings.
        3. **Numeric Outliers**:
           - Mathematical outlier detection using the Interquartile Range (IQR).
           - Negative checks on positive count fields.
        4. **Standard Constraints**:
           - If `Age` is found: bounds checked [0, 100].
           - If `email` is found: regex format validated.
           - Missing checks in `name` and `roll number`.
        """
    )
    
    st.markdown("---")
    st.markdown("### 🔑 API Secrets Configuration")
    st.markdown(
        """
        Configure your OpenRouter API Key by creating:
        - A `.streamlit/secrets.toml` file with `OPENROUTER_API_KEY="..."` OR
        - A `.env` file in the root folder with `OPENROUTER_API_KEY="..."`
        """
    )

# Main Panel Logic
if uploaded_file is not None:
    # 1. Read and validate CSV
    df, errors_text, preview_text = validate_csv(uploaded_file)
    
    if df is not None:
        # Display Preview
        st.markdown('<span class="section-title">📊 Dataset Preview</span>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=220)
        
        # Display column properties
        st.markdown('<span class="section-title">⚙️ Detected Column Attributes</span>', unsafe_allow_html=True)
        attributes_df = detect_dataset_attributes(df)
        st.dataframe(attributes_df, use_container_width=True, hide_index=True)
        
        # Call LLM helper
        with st.spinner("Anomalies scanning & OpenAI GPT recommendation generation in progress..."):
            attributes_text = attributes_df.to_string(index=False)
            ai_suggestions = get_openai_suggestions(errors_text, preview_text, attributes_text)
            
        # Display side-by-side results in Textboxes
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_area(
                label="Detected Errors",
                value=errors_text,
                height=400,
                help="Lists the validation warnings found programmatically by the rule engine."
            )
            
        with col2:
            st.text_area(
                label="AI Suggestions",
                value=ai_suggestions,
                height=400,
                help="Diagnosis, suggestions, and cleanup script generated by OpenRouter (Nex-AGI)."
            )
    else:
        st.error(errors_text)
else:
    # Landing / Welcome Page
    st.info("👈 Upload a CSV file in the sidebar to start scanning for quality errors and get AI recommendations!")
    
    # Show a brief preview banner of how it works
    st.markdown("### How It Works")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 1. Upload CSV")
        st.write("Drag and drop any CSV file. The app handles encoding variations (`utf-8`, `latin-1`, `cp1252`) and parsing errors automatically.")
    with col2:
        st.markdown("#### 2. Local Diagnostics")
        st.write("Our system immediately scans the schema, checks data types, infers column categories, and flags formatting anomalies programmatically.")
    with col3:
        st.markdown("#### 3. OpenRouter Repair")
        st.write("OpenRouter processes issues dynamically and returns structural diagnosis, correction steps, and a fully executable Pandas correction script.")
