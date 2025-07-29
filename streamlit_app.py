import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="User Study Survey", layout="wide")
st.title("📝 User Study Survey")

# === Inputs ===
name = st.text_input("1. What is your name?")
age = st.slider("2. What is your age?", 10, 100)
satisfaction = st.radio("3. How satisfied are you?",
                        ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very dissatisfied"])
feedback = st.text_area("4. Any additional feedback?")

# === Google Sheet Setup ===
def connect_to_worksheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("CREDENTIALS.json", scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("userstudy")  # name of the spreadsheet
    worksheet = spreadsheet.sheet1  # or use get_worksheet(index) if you have multiple tabs
    return worksheet

# === Submission ===
if st.button("Submit"):
    if name.strip() == "":
        st.warning("Please enter your name.")
    else:
        try:
            sheet = connect_to_worksheet()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([timestamp, name, age, satisfaction, feedback])
            st.success("✅ Thank you! Your response has been recorded.")
        except Exception as e:
            st.error(f"⚠️ Submission failed: {type(e).__name__} - {e}")
