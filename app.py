import streamlit as st
import requests

st.title("📄 Invoice AI Agent")

branch_id = st.text_input("Enter Branch ID")

file = st.file_uploader("Upload Invoice", type=["pdf","png","jpg"])

if st.button("Process Invoice"):
    if file and branch_id:

        response = requests.post(
            "https://invoice-ai-agent-nafo.onrender.com/process",
            files={"file": file},
            data={"branch_id": branch_id}
        )

        result = response.json()

        st.success("✅ Processed Successfully")
        st.write("Invoice No:", result["invoice_no"])
        st.write("Amount:", result["amount"])

    else:
        st.error("Please enter all details")