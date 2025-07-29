import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="User Study Survey", layout="wide")

st.title("📝 User Study Survey")

# === Survey Questions ===
name = st.text_input("1. What is your name?")
age = st.slider("2. What is your age?", 10, 100)
satisfaction = st.radio("3. How satisfied are you with the system?", 
                        ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very dissatisfied"])
feedback = st.text_area("4. Any additional feedback or comments?")

# === Save Responses ===
if st.button("Submit"):
    if name.strip() == "":
        st.warning("Please enter your name before submitting.")
    else:
        # Create directory if not exists
        os.makedirs("responses", exist_ok=True)

        # Create or append to CSV
        df = pd.DataFrame([{
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "age": age,
            "satisfaction": satisfaction,
            "feedback": feedback
        }])

        csv_path = "responses/survey_responses.csv"
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_path, index=False)

        st.success("✅ Thank you for your submission!")
