import os
import openai
import sqlite3
import pandas as pd
import datetime
import random

class Database:
    def __init__(self, db_name="sleepdata.db"):
# Connect to SQLite Database and create a database called sleepdata.db
# The cursor will write and read inside the database 
        """
        Initialization method for the Database class.
        It establishes a connection to the SQLite database.
        """
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name) 
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
# Create the results table if not exists
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_method TEXT,
            details TEXT,
            result TEXT,
            timestamp TEXT
        )
        """)
        self.conn.commit()

    def save_result(self, input_method, details, result):
        """
        Saves the result of the sleep apnea detection to the database.
        Args:
            input_method (str): The method used to get input (e.g., 'Sample Data', 'User Input').
            details (str): A description or file path related to the input.
            result (str): The result of the detection ('Positive' or 'Negative').
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
        INSERT INTO results (input_method, details, result, timestamp)
        VALUES (?, ?, ?, ?)
        """, (input_method, details, result, timestamp))
        self.conn.commit()

    def get_last_results(self, limit=10):
        """
        Fetches the last `limit` results from the database.
        Args:
            limit (int): The number of results to retrieve. Default is 10.
        Returns:
            list: List of tuples representing the results from the database.
        """
        self.cursor.execute(f"SELECT * FROM results ORDER BY id DESC LIMIT {limit}")
        return self.cursor.fetchall()

    def close(self):
        """Closes the database connection."""
        self.conn.close()

class SleepApneaDetector:
    def __init__(self):
        """
        Initialization method for the SleepApneaDetector class.
        It initializes the OpenAI API key, sets up placeholders for user input,
        and creates an instance of the Database class for managing results.
        """
# Telling OpenAI to use the gpt-3.5-turbo model
# Setting your API key so that it can talk to the AI model
        openai.api_key = "your_openai_api_key_here"

# Initialize database object
        self.db = Database()

# These are placeholders for the current input, method, and details curr = current
        self.curr_input = None
        self.curr_method = None
        self.curr_details = None
# Various ways the user can input the data
#--------------------------------------------------------------------------------
# 1. Sample Data File -- This will load an already preloaded sample which explain others data and sleep health
# so you can compare your data to it. Some will have sleep apena and some will not.
#--------------------------------------------------------------------------------
    def using_sample_data(self):
        """Loads preloaded sample data for analysis."""
        try:
            df = pd.read_csv("Sleep_health_and_lifestyle_dataset.csv")#...Loading in the sample data
            self.curr_input = df.iloc[[0]]   # First row
            self.curr_method = "Sample Data"
            self.curr_details = "Sleep_health_and_lifestyle_dataset.csv"
            print("Sample data loaded successfully.")
            self.run_detection() # <-- automatically run detection after loading
        except FileNotFoundError:
            print("Error: Sample data file not found.")
#--------------------------------------------------------------------------------
# 2. Upload Your Own Data File -- This will allow you to upload your own data file.
#    Each file will be organized and will breakdown the data.
# --------------------------------------------------------------------------------
    def upload_user_data(self):
        """Allows user to upload their own CSV data file."""
        path = input("Enter path to your CSV file: ").strip()
        if not os.path.exists(path):
            print("Error: File not found.")
            return
        try:
            df = pd.read_csv(path)
            self.curr_input = df.iloc[[0]]
            self.curr_method = "Upload File"
            self.curr_details = path
            print("File uploaded successfully.")
        except Exception as e:
            print(f"Error: Could not read file. {e}")
#---------------------------------------------------------------------------------------------------------------------
#3. Answer a Few Questions -- This will allow the user to answer a few questions about their sleep health and lifestyle.
#    Each question will be asked and the user will be able to answer them. The answers will be stored in a dataframe.
#    The dataframe will be used to run the detection. Each question will be asked in a loop until the user answers it.
#---------------------------------------------------------------------------------------------------------------------

    def answer_questions(self):
#Allows the user to answer a set of yes/no questions.
        try:
            questions = [
            "Do you snore loudly? (yes/no): ",
            "Do you feel tired during the day? (yes/no): ",
            "Has anyone said you stop breathing while asleep? (yes/no): ",
            "Do you wake up gasping or choking? (yes/no): ",
            "Do you have high blood pressure? (yes/no): ",
            "Do you frequently wake up feeling short of breath? (yes/no): ",
            "Do you have a dry mouth or sore throat when you wake up? (yes/no): ",
            "Do you often have trouble staying awake during the day? (yes/no): ",
            "Do you experience headaches upon waking? (yes/no): ",
            "Do you experience restless sleep or toss and turn frequently? (yes/no): ",
            "Have you had difficulty concentrating or memory problems during the day? (yes/no): ",
            "Do you have difficulty staying awake while driving or watching TV? (yes/no): ",
            "Have you ever been told you stop breathing while asleep? (yes/no): ",
            "Do you have a history of diabetes? (yes/no): ",
            "Do you have a family history of sleep apnea or other sleep disorders? (yes/no): ",
            "Have you been diagnosed with any other sleep disorders, such as insomnia? (yes/no): ",
            "Do you have heart disease or a history of heart problems? (yes/no): ",
            "Do you experience acid reflux or heartburn, especially at night? (yes/no): ",
            "Do you smoke or have a history of smoking? (yes/no): ",
            "Do you consume alcohol frequently? (yes/no): ",
            "Do you consume caffeine, especially in the late afternoon or evening? (yes/no): ",
            "Do you follow an irregular sleep schedule or work night shifts? (yes/no): ",
            "Do you have nasal congestion or difficulty breathing through your nose? (yes/no): "
            ]

            answers = []
            for q in questions:
                while True:
                    response = input(q).strip().lower()
                    if response in ["yes", "no"]:
                        answers.append(1 if response == "yes" else 0) #Error Handling for the yes and no answers nothing else will be accepted
                        break
                    else:
                        print("Please answer with 'yes' or 'no'.")

            self.curr_input = pd.DataFrame([answers])
            self.curr_method = "Answer Questions"
            self.curr_details = "User Input"
            print("Answers recorded successfully.")
        except Exception as e:
            print(f"Error: {e}")
#-----------------------------------------------------------------------------------------
# 4. Explain Result -- This will explain the result of the detection in simple terms.
#    The AI will determine if it says positive or negative and then explain what that means.
#    If says positive it means you are at risk that does not mean you gurantee you have it.
#    Please see a doctor for more information. AI can make mistakes.
#------------------------------------------------------------------------------------------
    def explain_result(self, result_text):
#Uses AI to explain what the detection result means in simple terms."""
        try:
            print("\n*AI* Generating explanation...")
            prompt = f"Explain in simple terms what '{result_text}' means in relation to sleep apnea."
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            explanation = response['choices'][0]['message']['content'].strip()
            print("\n[AI] Explanation:")
            print(explanation)
        except Exception as e:
            print(f"Error: {e}")
#-----------------------------------------------------------------------------------------
# 5. Run Detection -- This will run the detection on the input data and save the results to the database.
#    Also you can view results which will show you the last 10 results. And see and compare with others.
#------------------------------------------------------------------------------------------
    def run_detection(self):
#Analyzes the input data and determines if sleep apnea risk is Positive or Negative.
        if self.curr_input is None:
            print("No input found. Choose an input method first.")
            return
        try:
            print("\n*AI* Running detection...")
# Ask the AI model if the results from the input looks like an at risk
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Based on these sleep apnea related answers {self.curr_input.iloc[0].to_list()}, is the user 'Positive' or 'Negative' for sleep apnea risk? Just answer 'Positive' or 'Negative'."}],
                max_tokens=50,
                temperature=0.7
            )
            
            result_text = response['choices'][0]['message']['content'].strip()
            print(f"\nResult: {result_text}")

            # Save result to database
            self.db.save_result(self.curr_method, self.curr_details, result_text)

            # Explain the result
            self.explain_result(result_text)
        except Exception as e:
            print(f"Error: {e}")

    def view_results(self):
#Shows the last 10 results saved in the database.
        print("\nPrevious Results:")
        rows = self.db.get_last_results()
        if not rows:
            print("No records yet.")
            return
        for row in rows:
            print(f"ID: {row[0]}, Method: {row[1]}, Result: {row[3]}, Time: {row[4]}")  # This will show the ID, Method, Result, and Time in each row
        print("")
# Generate synthetic data based on the sample data
# This can be used to create a large dataset for testing or training purposes
    def roll_sleep_apnea_data(self, num_records):
#Generates synthetic sleep data based on existing sample data.
        try:
            df = pd.read_csv("Sleep_health_and_lifestyle_dataset.csv")
            synthetic_data = []
            for _ in range(num_records):
                synthetic_row = []
                for column in df.columns:
                    column_values = df[column].dropna().unique()  # Get the unique values for each column 
                    synthetic_row.append(random.choice(column_values))# Pick a random value from the column
                synthetic_data.append(synthetic_row)
            return synthetic_data
        except FileNotFoundError:
            print("Error: Sample data file not found.")
            return []
# Show the synthetic data in a readable format
    def display_synthetic_data(self, synthetic_data):
#Formats and displays synthetic data.
        if not synthetic_data:
            print("No synthetic data to display.")
            return

        headers = ["Person ID", "Gender", "Age", "Occupation", "Sleep Duration",  # These are the headers from the CSV file and get a grasp of what will be in the data
                   "Quality of Sleep", "Physical Activity Level", "Stress Level", 
                   "BMI Category", "Blood Pressure", "Heart Rate", 
                   "Daily Steps", "Sleep Disorder"]
# Dynamically calculate the column widths based on the headers and values
        column_widths = [len(str(header)) for header in headers]
        for row in synthetic_data:
            for i, val in enumerate(row):
                column_widths[i] = max(column_widths[i], len(str(val))) # Ensure values are converted to strings

        header_row = " | ".join([header.ljust(column_widths[i]) for i, header in enumerate(headers)])
        print(header_row)
        print("-" * len(header_row)) #Using "-" to separate the header from the data

        for row in synthetic_data:
            data_row = " | ".join([str(val).ljust(column_widths[i]) for i, val in enumerate(row)]) #the join method will join the data with the header and make it look nice.
            print(data_row)

        print("\nPress ENTER to return to the menu...") #input to return to the menu
        input()

    def main_menu(self):
        """Main interactive menu for the user."""
        while True:
            print("\n========================")
            print("Sleep Apnea Detector")
            print("========================")
            print("1. Use Sample Data File")
            print("2. Upload Your Own Data File")
            print("3. Answer a Few Questions")
            print("4. Run Detection")
            print("5. View Past Results")
            print("6. Generate Synthetic Data")
            print("7. Exit")

            choice = input("Select an option (1-7): ").strip()

            if choice == "1":
                self.using_sample_data()
            elif choice == "2":
                self.upload_user_data()
            elif choice == "3":
                self.answer_questions()
            elif choice == "4":
                self.run_detection()
            elif choice == "5":
                self.view_results()
            elif choice == "6":
                num_records = int(input("Enter the number of synthetic data records to generate: "))
                synthetic_data = self.roll_sleep_apnea_data(num_records)
                print(f"Generated {num_records} synthetic data records.")
                self.display_synthetic_data(synthetic_data)
            elif choice == "7":
                print("Goodbye!")
                break
            else:
                print("[!] Invalid input. Try again.")

        self.db.close()

# Start the program
if __name__ == "__main__":
    app = SleepApneaDetector()
    app.main_menu()
