import streamlit as st
import requests
from api import mock_api
from shared.models import CurrencyStrEnum, CreativeTypeStrEnum, CampaignStateStrEnum


API_URL = "http://localhost:8000"

st.title("Mocking Moloco Ad")
st.sidebar.title("Ad Manager")
page = st.sidebar.radio("Navigate", ['Upload Creative', 'Create Group', 'Manage Campaigns', 
                                     'Evaluate', "Creatives", "Creative Groups", "Campaigns",
                                     "Champion Groups"])

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
        selected = st.multiselect("Select 2 Creatives", list(options.keys()))
        submitted = st.form_submit_button("Add Group")
        if submitted and group_title:
            if len(selected) == 2:
                data = {"title": group_title, "description": description, "creative_ids": [options[s] for s in selected]}
                response = requests.post(f"{API_URL}/creative-groups", params=data)
                if response.ok:
                    st.success("Group created successfully.")
                else:
                    st.error(response.text)
            else:
                st.error("Select exactly 2 creatives for a group!")

elif page == 'Manage Campaigns':
    st.header("Attach Group To Campaigns")
    groups = requests.get(f"{API_URL}/creative-groups").json()
    group_opts = {f"{g['title']} (id {g['id']})": g['id'] for g in groups}
    campaigns = requests.get(f"{API_URL}/campaigns").json()
    campaign_opts = {f"{c['title']} (id {c['id']})": c['id'] for c in campaigns}

    select_campaign_title = st.selectbox("Campaign", list(campaign_opts.keys()))
    select_group_title = st.selectbox("Group to Attach", list(group_opts.keys()))
    if st.button("Attach Group"):
        cid = campaign_opts[select_campaign_title]
        gid = group_opts[select_group_title]
        response = requests.post(f"{API_URL}/campaigns/{cid}/attach", params={"group_id": gid})
        if response.ok:
            st.success(f"Group {select_group_title} attached to {select_campaign_title}")
        else:
            st.error(response.text)

    # for i, c in enumerate(campaigns.json()):
    #     st.write(f"{i+1}. {c['title']} ({c['enabling_state']}) ({c['state']}) (ID {c['id']})")
    
elif page == "Creatives":
    st.header("Current Creatives")
    response = requests.get(f"{API_URL}/creatives")
    for i, r in enumerate(response.json()):
        st.write(f"{i+1}. {r['title']} ({r['filename']}, ID {r['id']})")

elif page == "Creative Groups":
    st.header("Current Creative Groups")
    groups = requests.get(f"{API_URL}/creative-groups")
    creatives = requests.get(f"{API_URL}/creatives").json()
    for i, group in enumerate(groups.json()):
        expander = st.expander(f"{i+1}. {group['title']} (ID {group['id']})")
        for cid in group['creative_ids']:
            expander.write(c['title'] for c in creatives if c.get('id') == cid)

elif page == "Campaigns":
    st.header("Current Campaigns")
    campaigns = requests.get(f"{API_URL}/campaigns")
    groups = requests.get(f"{API_URL}/creative-groups").json()
    for i, campaign in enumerate(campaigns.json()):
        expander = st.expander(f"{i+1}. {campaign['title']} ({campaign['state']})")
        for gid in campaign['groups']:
            expander.write(f"{g['title']} ({campaign['impressions'][gid]})" for g in groups if g.get('id') == gid)

        col1, col2= st.columns(2)
        with col1:
            if st.button("Launch/Pause", key=f"launch_{campaign['id']}"):
                if campaign['state'] == CampaignStateStrEnum.PAUSED:
                    requests.post(f"{API_URL}/campaigns/{campaign['id']}/state", params={"state": CampaignStateStrEnum.ACTIVE})
                elif campaign['state'] == CampaignStateStrEnum.ACTIVE:
                    requests.post(f"{API_URL}/campaigns/{campaign['id']}/state", params={"state": CampaignStateStrEnum.PAUSED})
                st.rerun()
        with col2:
            if st.button("Reset", key=f"reset_{campaign['id']}"):
                requests.post(f"{API_URL}/campaigns/{campaign['id']}/reset")
                st.rerun()
                st.success(f"Reset {campaign['title']}")

    # Refresh button
    if st.button("Refresh", key="Refresh"):
        st.rerun()

elif page == "Champion Groups":
    st.header("Champion Groups")
    groups = requests.get(f"{API_URL}/creative-groups").json()
    champion_group_ids = requests.get(f"{API_URL}/champions").json()
    for i, gid in enumerate(champion_group_ids):
        st.write(f"{i+1}. {g['title']} (ID {g['id']})" for g in groups if g.get('id') == gid)
    