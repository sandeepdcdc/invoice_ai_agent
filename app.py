import streamlit as st
import requests
import time
import requests

import streamlit as st

st.set_page_config(layout="centered")

hide_streamlit = """
<style>
/* Hide header, menu, footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Hide "Hosted with Streamlit" */
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}
[data-testid="stStatusWidget"] {display: none !important;}
[data-testid="stAppViewContainer"] > div:nth-child(1) {display:none;}
</style>
"""

st.markdown("""
<div style="
    background-color:#0F63AC;
    padding:6px 10px;
    border-radius:6px;
    text-align:center;
    margin-bottom:12px;
">
    <span style="
        color:white;
        font-size:18px;
        font-weight:600;
    ">
        HMIS - Invoice Processing AI Agent
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Hide menu + footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Hide floating buttons */
[data-testid="stToolbar"] {display:none !important;}
[data-testid="stDecoration"] {display:none !important;}
[data-testid="stStatusWidget"] {display:none !important;}
button[kind="header"] {display:none !important;}
</style>

<script>
// Force remove floating elements (important)
const hideElements = () => {
    const elements = window.parent.document.querySelectorAll('[data-testid="stDecoration"], [data-testid="stToolbar"], iframe');
    elements.forEach(el => el.remove());
};
setInterval(hideElements, 1000);
</script>
""", unsafe_allow_html=True)

button_style = """
<style>
div.stButton > button {
    background-color: #0F63AC;
    color: white;
    border-radius: 8px;
    height: 45px;
    width: 100%;
    font-weight: bold;
}

div.stButton > button:hover {
    background-color: #0c4f8a;
    color: white;
}
</style>
"""
st.markdown(button_style, unsafe_allow_html=True)

# st.title("📄 Invoice AI Agent")

branch_id = st.text_input("Enter Branch ID")

file = st.file_uploader("Upload Invoice", type=["pdf","png","jpg"])

if st.button("Process Invoice"):

    if file and branch_id:

        status_placeholder = st.empty()
        status_placeholder.info("⏳ Connecting to server...")

        try:
            response = requests.post(
                "https://invoice-ai-agent-nafo.onrender.com/process",
                files={"file": file},
                data={"branch_id": branch_id},
                timeout=120
            )

            # REMOVE LOADING MESSAGE
            status_placeholder.empty()

            # st.write("Status Code:", response.status_code)
            if st.checkbox("Show Debug Info"):
             st.write("Status Code:", response.status_code)

            if response.status_code != 200:
                st.error("❌ API Error")
                st.write(response.text)
                st.stop()

            try:
                result = response.json()
            except:
                st.error("Invalid JSON response")
                st.write(response.text)
                st.stop()

            invoice_no = result.get("invoice_no", "Not Found")
            amount = result.get("amount", "0")

            st.success("✅ Processed Successfully")
            st.write("Invoice No:", invoice_no)
            st.write("Amount:", amount)

        except requests.exceptions.RequestException as e:
            status_placeholder.empty()
            st.error("🚨 Server not reachable")
            st.write(str(e))

    else:
        st.error("Please enter all details")