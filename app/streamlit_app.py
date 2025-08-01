import streamlit as st
import requests
from api import mock_api


API_URL = "http://localhost:8000"

st.title("Mocking Moloco Ad")
st.sidebar.title("Ad Creative Manager")
page = st.sidebar.radio("Navigate", ['Upload Creative', 'Create Group', 'Manage Campaigns', 'Evaluate', "Creatives"])

if page == 'Upload Creative':
    st.header("Upload New Creative")
    with st.form("creative_form"):
       title = st.text_input("Creative Title")
       type = st.selectbox("Type", ["IMAGE", "VIDEO", "HTML"])
       submitted = st.form_submit_button("Add Creative")

       if submitted and title and type:
           query = {"title": title, "type": type}
           response = requests.post(f"{API_URL}/creatives", params=query)
           if response.ok:
               st.success(f"{response.json()['title']} uploaded (ID {response.json()['id']})")
           else:
               st.error(response.text)

elif page == "Creatives":
    st.header("Current Creatives")
    response = requests.get(f"{API_URL}/creatives")
    for i, r in enumerate(response.json()):
        st.write(f"{i+1}. {r['title']} (ID {r['id']})")