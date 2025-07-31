import streamlit as st
from api import mock_api

st.title("Mocking Moloco Ad")

st.header("Step 1: Add New Creative")
with st.form("add_creative_form"):
    name = st.text_input("Creative Concept Name")
    orientation = st.selectbox("Type", ["Portrait", "Landscape"])
    file_name = st.text_input("Video File Name (simulated)")
    submit = st.form_submit_button("Add Creative")
    if submit and name and file_name:
        creative = mock_api.add_creative(name, orientation, file_name)
        st.success(f"Added creative: {creative['name']} ({creative['orientation']})")


# 2. Show creatives (and so on for groups/campaigns/champions)
st.header("Current Creatives")
for creative in mock_api.creatives:
    st.write(f"{creative['name']} ({creative['orientation']}) - {creative['file_name']}")