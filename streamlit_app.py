import streamlit as st
from PIL import Image
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import tempfile
import os

st.set_page_config(page_title="Visual Survey", layout="wide")
st.title("🧪 Visual Figure Survey")

# === Config ===
q_folder = os.path.join(os.path.dirname(__file__), "questions")
num_questions = 2  # Update this to 20 for full survey
options = ["A", "B", "C", "D", "E", "F"]

# === State Init ===
if "current_q" not in st.session_state:
    st.session_state.current_q = 1

if "responses" not in st.session_state:
    st.session_state.responses = {}

# === Google Sheets Connector ===
@st.cache_resource
def get_worksheet():
    """Cached Google Sheets connection"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    json_creds = st.secrets["gcp"]["gsheet_credentials"]
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmpfile:
        tmpfile.write(json_creds)
        tmpfile.flush()
        creds = ServiceAccountCredentials.from_json_keyfile_name(tmpfile.name, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("userstudy")  # Your actual sheet name
    worksheet = spreadsheet.sheet1
    return worksheet

# === Helper Functions ===
def is_question_completed(q_id):
    """Check if a question has been answered"""
    return len(st.session_state.responses.get(q_id, [])) > 0

def get_completion_status():
    """Get completion status for all questions - cached version"""
    if "completion_cache" not in st.session_state:
        completed = sum(1 for i in range(1, num_questions + 1) 
                       if is_question_completed(f"q{i}"))
        st.session_state.completion_cache = completed
    return st.session_state.completion_cache, num_questions

def update_completion_cache():
    """Update completion cache when responses change"""
    if "completion_cache" in st.session_state:
        del st.session_state.completion_cache

@st.dialog("📋 Review Your Answers")
def show_confirmation_dialog():
    st.markdown("**Please review your selections before submitting:**")
    
    # Display all answers in a clean format
    for i in range(1, num_questions + 1):
        q_id = f"q{i}"
        answers = st.session_state.responses.get(q_id, [])
        answer_text = ", ".join(answers) if answers else "Not answered"
        status_icon = "✅" if answers else "❌"
        st.markdown(f"{status_icon} **Question {i}:** {answer_text}")
    
    col1, col2 = st.columns([1, 1])


    if "submitted" not in st.session_state or not st.session_state.submitted:
        st.info("Don't forget to submit your responses!")
    else:
        st.success("Submission success!")

    if col1.button("✅ Confirm & Submit", type="primary"):
        try:
            sheet = get_worksheet()
            row = [datetime.now().isoformat(), name]
            for i in range(1, num_questions + 1):
                ans = ",".join(st.session_state.responses.get(f"q{i}", []))
                row.append(ans)
            sheet.append_row(row)
            st.success("Submission success!") 
            # Set submitted state to hide warning
            st.session_state.submitted = True
            # Clear session state to prevent going back
            st.session_state.clear()
            st.rerun()
        except Exception as e:
            st.error(f"⚠️ Submission failed: {type(e).__name__} - {e}")
    
    if col2.button("❌ Cancel"):
        st.rerun()

# === Navigation and Submit Section ===
nav_col, submit_col = st.columns([3, 1])

with nav_col:
    st.markdown("### Navigation")
    completed, total = get_completion_status()
    st.markdown(f"**Progress: {completed}/{total} questions completed**")

    # Create navigation buttons with completion status
    nav_cols = st.columns(10)  # adjust based on how many buttons per row

    for i in range(1, num_questions + 1):
        col = nav_cols[(i - 1) % len(nav_cols)]
        q_id = f"q{i}"
        is_completed = is_question_completed(q_id)
        is_current = i == st.session_state.current_q
        
        # Button styling based on status
        if is_current:
            button_label = f"➡️ {i}"
            button_color = "primary"
        elif is_completed:
            button_label = f"✅ {i}"
            button_color = "secondary"
        else:
            button_label = f"🔲 {i}"
            button_color = "secondary"
        
        if col.button(button_label, key=f"nav_{i}", type=button_color):
            if st.session_state.current_q != i:  # Only rerun if actually changing questions
                st.session_state.current_q = i
                st.rerun()

with submit_col:
    st.markdown("### Submit")
    st.markdown("""
    <div style="
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
        color: #856404;
    ">
    ⚠️ Don't forget to submit your responses!
    </div>
    """, unsafe_allow_html=True) 


    name = st.text_input("Enter your name (or ID) to submit:", key="name_input")
    
    # Check if all questions are completed
    all_completed = all(is_question_completed(f"q{i}") for i in range(1, num_questions + 1))
    
    # Submit button
    if st.button("📤 Submit Responses", disabled=not all_completed or name.strip() == "", key="submit_btn"):
        if name.strip() == "":
            st.warning("Please enter your name before submitting.")
        elif not all_completed:
            st.warning("Please complete all questions before submitting.")
        else:
            show_confirmation_dialog()
    
    # Show completion status right below submit
    completed, total = get_completion_status()
    if completed == total:
        st.success(f"🎉 All {total} questions completed!")
    else:
        st.info(f"📝 {completed}/{total} questions completed.")

st.markdown("---")

# === Display Question ===
q = st.session_state.current_q
q_id = f"q{q}"
img_path = os.path.join(q_folder, f"{q_id}.png")

st.markdown(f"### Question {q} of {num_questions}")

# Create two columns: left for image, right for options
img_col, options_col = st.columns([3, 2])

with img_col:
    # Adjust image size for MacBook 14 screen (approximately 1200px width)
    if not os.path.exists(img_path):
        st.warning(f"Missing image: {q_id}.png")
    else:
        img = Image.open(img_path)
        # Calculate appropriate width to fit screen without scrolling
        # MacBook 14 has ~1200px width, leave space for margins and options
        max_width = 600
        st.image(img, caption=f"{q_id}.png", width=max_width)

with options_col:
    st.markdown("**Select all applicable options from A–F, or 'None of the above':**")

    # Restore or initialize checkbox state
    if q_id not in st.session_state.responses:
        st.session_state.responses[q_id] = []

    selected_options = []
    cols = st.columns(2)

    for idx, opt in enumerate(options):
        with cols[idx % 2]:
            current_value = opt in st.session_state.responses[q_id]
            checked = st.checkbox(
                opt,
                key=f"{q_id}_{opt}",
                value=current_value
            )
            if checked:
                selected_options.append(opt)

    with cols[1]:
        none_selected = st.checkbox(
            "None of the above",
            key=f"{q_id}_none",
            value=("None of the above" in st.session_state.responses[q_id])
        )

    # Save current selections to session state
    new_response = ["None of the above"] if none_selected else selected_options
    # Only update if response actually changed
    if st.session_state.responses.get(q_id, []) != new_response:
        st.session_state.responses[q_id] = new_response
        update_completion_cache()  # Update cache when responses change

    
    if st.button("Proceed"):
        # Validation only when button is clicked
        if len(selected_options) == 0 and not none_selected:
            st.error("⚠️ Please select at least one option or 'None of the above'.")
        elif len(selected_options) > 0 and none_selected:
            st.error("⚠️ Cannot select both A–F and 'None of the above'.")
        else:
            # Next/Submit button
            if q < num_questions:
                st.session_state.current_q = q + 1
                st.rerun()
            else:
                st.success("✅ All questions completed! You can submit now. Go to the submit section above ⬆️.")

