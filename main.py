
import streamlit as st
import numpy as np
import pandas as pd
import pickle
import xgboost
import sqlite3
from datetime import datetime

# Function to get database connection
def get_db_connection():
    return sqlite3.connect('loan_data.db')

# Load the machine learning model
with open("model.pkl", 'rb') as f:
    model = pickle.load(f)

# Database connection (SQLite for simplicity)
conn = sqlite3.connect('loan_data.db')
c = conn.cursor()

import sqlite3
from datetime import datetime

# Function to initialize the database
def initialize_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS loan_applications (
        customer_id TEXT,
        age INTEGER,
        income FLOAT,
        home_ownership TEXT,
        loan_amount FLOAT,
        loan_interest_rate FLOAT,
        credit_score INTEGER,
        previous_defaults TEXT,
        loan_status TEXT,
        application_date TEXT
    )
    """)
    conn.commit()
    conn.close()

# Call this function at the start of your script
initialize_db()


# Display app description at the top right side
st.sidebar.header("Loan Status Prediction App")
st.sidebar.markdown(""" This app is used to predict loan approval status based on user-provided financial and personal details using a machine learning model.


**Declaration**  

This application is developed for **educational purposes** to demonstrate the use of machine learning techniques in predicting loan approval statuses. It utilizes a **loan dataset** with key financial and personal features such as age, income, credit score, loan amount, and more to highlight the predictive capabilities of AI models.  

The app serves as an interactive tool for understanding the importance of various features in loan approval, showcasing insights into how financial institutions evaluate loan applications. It emphasizes learning and exploration of data science concepts, feature importance, and real-world application scenarios in the domain of banking and finance.  

The dataset and predictions are used strictly for **educational and research purposes** and should not be treated as financial advice or a substitute for professional evaluation.

# """)

# In predicting loan approval, the most important factors are:

# 1. **Previous Loan Defaults (22.58%)**
# 2. **Loan-to-Income Ratio (16.47%)**:
# 3. **Loan Interest Rate (15.79%)**: 
# 4. **Income (12.54%)**:
# 5. **Loan Amount (5.91%)**:
# 6. **Credit Score (5.58%)**:
# 7. **Home Ownership (6.86%)**:
# 8. **Age (2.95%)**: 

# In short, financial behavior and capacity to repay (like previous defaults and income) are the key determinants of loan approval.

# App branding
st.title("Loan Status Prediction 💰💹")
st.subheader("For Bank & Loan Request Customers")

# Input customer ID
st.subheader("Customer Details")
customer_id = st.text_input("Enter Customer ID", placeholder="E.g., BANK12345...")

# Input fields
col1, col2 = st.columns(2)
with col1:
    person_age = st.number_input("Age of the person", min_value=18, max_value=100, value=30)
with col2:
    person_income = st.number_input("Annual income", min_value=0.0)

# Condition 4: Highlight annual income check
if person_income < 30000:
    st.warning("Note: Annual income is below the threshold of 30,000 for loan approval.")

col3 = st.columns(1)[0]
with col3:
    person_home_ownership = st.selectbox("Home ownership status", ("RENT", "MORTGAGE", "OWN", "OTHER"))

# Condition 5: Highlight home ownership check
if person_home_ownership not in ["OWN", "MORTGAGE"]:
    st.warning("Note: Homeownership status may reduce the chances of loan approval.")

col4 = st.columns(1)[0]
with col4:
    loan_amnt = st.number_input("Loan amount requested")

col5 = st.columns(1)[0]
with col5:
    loan_int_rate = st.number_input("Loan interest rate", min_value=5.42, max_value=20.00, help="Enter the loan interest rate (e.g., 9.5%)")

# Condition 3: Highlight interest rate check
if loan_int_rate < 10.0:
    st.warning("Loan interest rate is below the threshold of 10%, improving the chance of approval.")

col6 = st.columns(1)[0]
with col6:
    if person_income > 0:  # Prevent division by zero
        loan_percent_income = loan_amnt / person_income  # Calculate loan amount as a percentage of income
    else:
        loan_percent_income = 0  # Set to 0 if income is 0 to avoid division by zero
    
    st.write(f"Loan amount as a percentage of income: {loan_percent_income * 100:.2f}%")

# Condition 2: Highlight loan percent income check
if loan_percent_income > 0.4:
    st.warning("Loan amount exceeds 40% of income, which may result in rejection.")


col7, col8 = st.columns(2)
with col7:
    credit_score = st.number_input("Credit score of the person", min_value=500, max_value=950)

# Condition 6: Highlight credit score check
if credit_score < 600:
    st.warning("Credit score is below 600, which reduces the chances of loan approval.")

with col8:
    previous_loan_defaults_on_file = st.selectbox("Indicator of previous loan defaults", ("No", "Yes"))

# Condition 1: Highlight previous loan defaults check
if previous_loan_defaults_on_file == "Yes":
    st.warning(" \"No\" previous loan defaults detected, improving the chances of loan approval.")

home_ownership_map = {"RENT": 0, "MORTGAGE": 1, "OWN": 2, "OTHER": 3}
previous_default_map = {"No": 0, "Yes": 1}

# Map categorical variables to numeric values
person_home_ownership = home_ownership_map[person_home_ownership]
previous_loan_defaults_on_file = previous_default_map[previous_loan_defaults_on_file]

# Create input array for prediction
input_data = [
    person_age,
    person_income,
    person_home_ownership,
    loan_amnt,
    loan_int_rate,
    loan_percent_income,
    credit_score,
    previous_loan_defaults_on_file
]

# Predict loan status
if st.button("Predict Loan Status"):
    if customer_id.strip() == "":
        st.error("Please enter a valid Customer ID.")
    else:
        prediction = model.predict([input_data])
        loan_status = "Approved ✅" if prediction[0] == 1 else "Rejected ❌"
        st.success(f"Loan Status: {loan_status}")
        
        # Save the application data to the database
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
        INSERT INTO loan_applications (
            customer_id, age, income, home_ownership, loan_amount, loan_interest_rate, 
            credit_score, previous_defaults, loan_status, application_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id, person_age, person_income, person_home_ownership, loan_amnt, 
            loan_int_rate, credit_score, previous_loan_defaults_on_file, loan_status, 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()
        st.success("Application data saved successfully!")
