# AI-Powered-Sleep-Apnea-Detection

💤 AI-Powered Sleep Apnea Detection Tool
This project is an intelligent application that uses OpenAI's GPT-3.5 model to analyze sleep health data and assess the risk of sleep apnea. It supports multiple input methods and provides clear, actionable results for users or healthcare professionals.

🚀 Features
AI-Powered Analysis
Evaluates sleep apnea risk using natural language inputs and structured data via GPT-3.5.

Flexible Input Options
Accepts:

Direct user prompts

Uploaded CSV files

Sample data (for testing/demo)

Automated Data Preprocessing
Uses Pandas to clean and structure input data for consistent AI analysis.

Local History Tracking
Stores results in a local SQLite database with timestamps and input types for easy future reference.

User-Friendly Interface
Simple and intuitive prompts for both technical and non-technical users.

📂 Project Structure
plaintext
├── app.py                # Main application logic
├── model.py              # GPT-3.5 interaction handler
├── database.py           # SQLite storage manager
├── utils.py              # Helper functions (e.g., data preprocessing)
├── templates/            # HTML templates (if web-based UI)
├── data/                 # Sample and uploaded CSVs
├── results.db            # Local SQLite database
└── README.md             # Project documentation
🛠️ Setup
Clone the repository

bash
git clone https://github.com/your-username/sleep-apnea-ai.git
cd sleep-apnea-ai
Install dependencies

bash
pip install -r requirements.txt
Add your OpenAI API key

Create a .env file or directly modify the config section in model.py.

Run the application

bash
python app.py
📊 Sample Input (CSV)
csv
Copy
Edit
Age,BMI,Sleep Duration,Snoring Frequency,Stress Level
45,32.5,5.5,High,Moderate
📦 Technologies Used
Python 3.10+

OpenAI GPT-3.5

Pandas

SQLite

Flask (optional for UI)

📌 Disclaimer
This tool is for educational and experimental purposes only. It is not a substitute for professional medical advice or diagnosis.
