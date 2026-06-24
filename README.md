# 🚀 Data Quality Agent with Auto-Fix Suggestions

## 🌐 Live Demo

🔗 Live Application:  
https://data-quality-agent-fxqbvdy8jwulc6u48appxtz.streamlit.app/

## 📂 GitHub Repository

🔗 Repository Link:  
https://github.com/nanepalli/data-quality-agent

---

## 📌 Project Overview

Data Quality Agent is a web-based application developed using Python and Streamlit that helps users identify, analyze, and automatically fix common data quality issues in datasets.

The application supports CSV and Parquet file formats and performs quality checks based on configurable YAML rules. Users can upload datasets, view detected issues, calculate data quality scores, apply automatic fixes, and download cleaned data.

This project demonstrates practical applications of Data Engineering, Data Analytics, and Data Quality Management concepts.

---

## 🎯 Objectives

- Improve dataset quality before analysis.
- Detect common data quality issues automatically.
- Provide an easy-to-use interface for non-technical users.
- Generate quality reports.
- Apply automatic fixes wherever possible.

---

## ✨ Features

### File Upload Support
- Upload CSV files
- Upload Parquet files

### Data Quality Checks
- Missing value detection
- Duplicate record detection
- Invalid email detection
- Negative value detection
- Rule-based validation

### Auto-Fix Functionality
- Fill missing values
- Remove duplicate records
- Clean invalid data
- Generate corrected datasets

### Reporting
- Data quality score
- Issue summary
- Validation results
- Download cleaned dataset

### User Interface
- Built with Streamlit
- Interactive dashboard
- Easy file upload and download

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|----------|
| Python | Programming Language |
| Pandas | Data Processing |
| Streamlit | User Interface |
| YAML | Rule Configuration |
| PyArrow | Parquet Support |
| GitHub | Version Control |
| VS Code | Development Environment |

---

## 📁 Project Structure

```text
data-quality-agent/
│
├── app.py
├── checker.py
├── fixer.py
├── ai_helper.py
├── convert.py
├── rules.yaml
├── requirements.txt
├── sample.csv
├── sample.parquet
├── report.txt
└── README.md
```

---

## ⚙️ Installation Guide

### Step 1: Clone Repository

```bash
git clone https://github.com/nanepalli/data-quality-agent.git
cd data-quality-agent
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run Application

```bash
streamlit run app.py
```

---

## 🚀 How to Use

### Upload Dataset

1. Open the application.
2. Upload a CSV or Parquet file.
3. Click Analyze.

### View Results

The system displays:

- Data Quality Score
- Missing Values
- Duplicate Records
- Invalid Emails
- Negative Values

### Apply Auto-Fix

1. Click Auto Fix.
2. Review cleaned dataset.
3. Download corrected file.

---

## 📊 Sample Workflow

1. Upload dataset
2. Analyze data quality
3. View detected issues
4. Apply automatic fixes
5. Download cleaned data
6. Use cleaned data for analytics

---

## 📷 Screenshots

### Home Page

Upload datasets using the file uploader.

*(Add screenshot here later)*

### Data Quality Report

View detected issues and quality score.

*(Add screenshot here later)*

### Auto Fix Results

Download cleaned datasets after corrections.

*(Add screenshot here later)*

---

## 📈 Benefits

- Saves manual data cleaning effort
- Improves data reliability
- Reduces data errors
- Enhances analytics accuracy
- Easy to use for beginners

---

## 🔮 Future Enhancements

- AI-based recommendations
- Advanced profiling dashboard
- Data visualization
- Database connectivity
- Real-time quality monitoring
- Automated report generation

---

## 🎓 Academic Relevance

This project demonstrates concepts from:

- Data Engineering
- Data Analytics
- Data Science
- Data Quality Management
- Python Programming
- Software Development

It can be used as:

- Mini Project
- Academic Project
- Internship Project
- Portfolio Project

---

## 👩‍💻 Author

### Nanepalli

B.Tech Student

Project Title: **Data Quality Agent with Auto-Fix Suggestions**

GitHub Profile:  
https://github.com/nanepalli

---

## 📜 License

This project is developed for educational, academic, and learning purposes.

---

## ⭐ Support

If you found this project useful:

⭐ Star the repository

🔗 Share the project

💡 Contribute improvements

---

## 🌟 Live Application

👉 https://data-quality-agent-fxqbvdy8jwulc6u48appxtz.streamlit.app/
