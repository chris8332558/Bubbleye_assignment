import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
from shared.models import CampaignStateStrEnum


API_URL = "http://localhost:8000"

st.title("Mocking Moloco Ad")
st.sidebar.title("Ad Manager")

page = st.sidebar.radio("Navigate", 
                         ['Upload Creative', 
                         'Create Group', 
                         'Manage Campaigns',
                         'Creatives', 
                         'Creative Groups', 
                         'Campaigns', 
                         'Champion Groups'
                         ])


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

elif page == "Create Group":
    st.header("Create Group")
    with st.form("creative_group_form"):
        creatives = requests.get(f"{API_URL}/creatives").json()
        options = {f"{c['title']} (ID {c['id']})": c['id'] for c in creatives}
        group_title = st.text_input("Group Title")
        description = st.text_input("Description")
        selected = st.multiselect("Select Creatives", list(options.keys()))
        submitted = st.form_submit_button("Add Group")
        if submitted and group_title:
            if len(selected) > 0:
                # Query Parameters for the API call
                data = {"title": group_title, "description": description, "creative_ids": [options[s] for s in selected]}
                response = requests.post(f"{API_URL}/creative-groups", params=data)
                if response.ok:
                    st.success("Group created successfully.")
                else:
                    st.error(response.text)
            else:
                st.error("Please select creatives for a group!")

elif page == 'Manage Campaigns':
    st.header("Manage Campaigns")
    groups = requests.get(f"{API_URL}/creative-groups").json()
    group_opts = {g['id']: g for g in groups}
    group_title_to_id = {g['title']: g['id'] for g in groups}

    campaigns = requests.get(f"{API_URL}/campaigns").json()
    campaign_opts = {c['id']: c for c in campaigns}
    campaign_title_to_id = {c['title']: c['id'] for c in campaigns}

    select_campaign_title = st.selectbox("Campaign", [c['title'] for c in campaign_opts.values()])
    select_campaign_id = campaign_title_to_id[select_campaign_title] 
    
    # Show the groups in the selected campaign
    st.write("Groups:")
    col1, col2 = st.columns(2)
    for gid in campaign_opts[select_campaign_id]['groups']:
        with col1:
            st.write(f"{g['title']}" for g in groups if g.get('id') == gid)
        with col2:
            if st.button("Remove", key=f"{select_campaign_id}_{gid}"):
                requests.post(f"{API_URL}/campaigns/{select_campaign_id}/remove", params={"group_id": gid})
                st.rerun()
                st.success(f"Removed group")

    # Only show the groups not in the selected campaign in the selectbox
    filtered_group_ids = [g for g in group_opts.keys() if g not in campaign_opts[select_campaign_id]['groups']]
    filtered_groups = {k: v for k, v in group_opts.items() if k in filtered_group_ids}
    select_group_title = st.selectbox("Group to Attach", [g['title'] for g in filtered_groups.values()])
    if select_group_title:
        select_group_id = group_title_to_id[select_group_title]

    if st.button("Attach Group"):
        response = requests.post(f"{API_URL}/campaigns/{select_campaign_id}/attach", params={"group_id": select_group_id})
        if response.ok:
            st.success(f"Group {select_group_title} attached to {select_campaign_title}")
        else:
            st.error(response.text)
        st.rerun()

    
elif page == "Creatives":
    # List the creatives
    st.header("Current Creatives")
    response = requests.get(f"{API_URL}/creatives")
    for i, r in enumerate(response.json()):
        st.write(f"{i+1}. {r['title']} ({r['filename']}) (ID {r['id']})")

elif page == "Creative Groups":
    # List the Creative Groups
    st.header("Current Creative Groups")
    groups = requests.get(f"{API_URL}/creative-groups")
    creatives = requests.get(f"{API_URL}/creatives").json()
    for i, group in enumerate(groups.json()):
        expander = st.expander(f"{i+1}. {group['title']} (ID {group['id']})")
        expander.write("Creatives:")
        for cid in group['creative_ids']:
            expander.write(c['title'] for c in creatives if c.get('id') == cid)

elif page == "Campaigns":
    # List the Campaigns, and add Launch/Pause and Reset buttons for each campaign
    st.header("Current Campaigns")
    campaigns = requests.get(f"{API_URL}/campaigns")
    groups = requests.get(f"{API_URL}/creative-groups").json()
    for i, campaign in enumerate(campaigns.json()):
        expander = st.expander(f"{i+1}. {campaign['title']} ({campaign['state']})")
        expander.write("Groups (impressions):")
        for gid in campaign['groups']:
            expander.write(f"{g['title']} ({campaign['impressions'][gid]})" for g in groups if g.get('id') == gid)

        col1, col2= st.columns(2)
        with col1:
            if st.button("Launch/Pause", key=f"launch_{campaign['id']}"):
                if len(campaign['groups']) == 0:
                    st.error("No groups in the campaign")
                elif campaign['state'] == CampaignStateStrEnum.PAUSED:
                    requests.post(f"{API_URL}/campaigns/{campaign['id']}/launch")
                    st.rerun()
                elif campaign['state'] == CampaignStateStrEnum.ACTIVE:
                    requests.post(f"{API_URL}/campaigns/{campaign['id']}/pause")
                    st.rerun()
        with col2:
            if st.button("Reset", key=f"reset_{campaign['id']}"):
                requests.post(f"{API_URL}/campaigns/{campaign['id']}/reset")
                requests.post(f"{API_URL}/campaigns/{campaign['id']}/pause")
                st.rerun()
                st.success(f"Reset {campaign['title']}")

    # Refresh button for monitoring latest impressions
    if st.button("Refresh", key="Refresh"):
        st.rerun()

elif page == "Champion Groups":
    # List the champioin creative groups
    st.header("Champion Groups")
    groups = requests.get(f"{API_URL}/creative-groups").json()
    champion_group_ids = requests.get(f"{API_URL}/champions").json()
    for i, gid in enumerate(champion_group_ids):
        st.write(f"{i+1}. {g['title']} (ID {g['id']})" for g in groups if g.get('id') == gid)
    