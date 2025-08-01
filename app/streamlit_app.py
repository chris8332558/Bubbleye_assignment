import streamlit as st
import requests



API_URL = "http://localhost:8000"

st.title("Mocking Moloco Ad")
st.sidebar.title("Ad Creative Manager")
page = st.sidebar.radio("Navigate", ['Upload Creative', 'Create Group', 'Manage Campaigns', 'Evaluate', "Creatives"])

if page == 'Upload Creative':
    st.header("Upload New Creative")
    with st.form("creative_form"):
       title = st.text_input("Creative Title")
       type = st.selectbox("Type", ["IMAGE", "VIDEO", "HTML"])
       submitted = st.form_submit_button("Submit")

       if submitted and title and type:
           query = {"title": title, "type": type}
           response = requests.post(f"{API_URL}/creatives", params=query)
           if response.ok:
               st.success(f"Creative uploaded (ID {response.json()['id']})")
           else:
               st.error(response.text)

# st.header("Step 1: Add New Creative")
# with st.form("add_creative_form"):
#     name = st.text_input("Creative Concept Name")
#     orientation = st.selectbox("Type", ["Portrait", "Landscape"])
#     file_name = st.text_input("Video File Name (simulated)")
#     submit = st.form_submit_button("Add Creative")
#     if submit and name and file_name:
#         creative = mock_api.add_creative(name, orientation, file_name)
#         st.success(f"Added creative: {creative['name']} ({creative['orientation']})")


# # 2. Show creatives (and so on for groups/campaigns/champions)
# st.header("Current Creatives")
# for creative in mock_api.creatives:
#     st.write(f"{creative['name']} ({creative['orientation']}) - {creative['file_name']}")