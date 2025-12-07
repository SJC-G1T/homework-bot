import streamlit as st
from openai import OpenAI
import json
import os
from datetime import datetime
import uuid

# 1. PAGE CONFIG
st.set_page_config(page_title="Midnight's Magic Hut", page_icon="🐈‍⬛", layout="wide")

# 2. MAGIC UI (CSS)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom right, #2e1a47, #0e0b16);
        color: #e0d4fc;
    }
    .stButton > button {
        width: 100%;
        height: 60px;
        border-radius: 12px;
        font-size: 18px;
        font-weight: bold;
        background-color: #5c3a9e;
        color: white;
        border: 2px solid #9b72cf;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #7b52c4;
        border-color: #d8b4fe;
        transform: scale(1.02);
    }
    header {background: rgba(0,0,0,0) !important;}
    .block-container {padding-top: 1rem;}
</style>
""", unsafe_allow_html=True)

# 3. HISTORY MANAGER
HISTORY_FILE = "midnight_history.json"

def load_all_history():
    if not os.path.exists(HISTORY_FILE):
        return {"Hope": [], "Rose": []}
    with open(HISTORY_FILE, "r") as f:
        try:
            data = json.load(f)
            if isinstance(data, list): return {"Hope": [], "Rose": []}
            return data
        except:
            return {"Hope": [], "Rose": []}

def save_current_chat(messages, session_id, user_name):
    data = load_all_history()
    user_history = data.get(user_name, [])
    found = False
    for session in user_history:
        if session.get("id") == session_id:
            session["messages"] = messages
            found = True
            break
    if not found:
        new_session = {
            "id": session_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "messages": messages
        }
        user_history.append(new_session)
    data[user_name] = user_history
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def delete_user_history(user_name):
    data = load_all_history()
    data[user_name] = [] 
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# 4. SAFETY ENGINE
def check_safety(client, user_text):
    try:
        response = client.moderations.create(input=user_text)
        result = response.results[0]
        if result.flagged:
            categories = [cat for cat, val in result.categories.model_dump().items() if val]
            return False, f"Flagged for: {', '.join(categories)}"
        return True, "Safe"
    except Exception as e:
        print(f"Moderation Error: {e}")
        return True, "Safe"

# 5. INIT STATE
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "profile" not in st.session_state:
    st.session_state.profile = "Rose"
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

# 6. SIDEBAR (SECURITY GATE)
with st.sidebar:
    st.header("🔮 Wizard Settings")
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    api_input = st.text_input("Spell Password (API Key)", type="password", value=st.session_state.api_key)
    if api_input:
        st.session_state.api_key = api_input

# 7. SECURITY STOP
if not st.session_state.api_key:
    st.title("🐈‍⬛ Midnight the Mentor")
    st.warning("⚠️ The crystal ball is locked. Please enter the Password (API Key) in the sidebar.")
    st.stop()

# 8. SIDEBAR CONTENT
with st.sidebar:
    st.markdown("---")
    current_user = st.session_state.profile
    st.subheader(f"📜 {current_user}'s Scrolls")
    
    all_data = load_all_history()
    user_chats = all_data.get(current_user, [])
    
    if user_chats:
        if st.checkbox(f"Show {current_user}'s Past Work"):
            for chat in reversed(user_chats[-5:]): 
                if len(chat['messages']) > 1:
                    with st.expander(f"{chat['timestamp']}"):
                        for m in chat['messages']:
                            if m['role'] != 'system':
                                name = "Midnight" if m['role'] == "assistant" else current_user
                                st.write(f"**{name}:** {m['content']}")
    else:
        st.caption("No scrolls found yet.")

    st.markdown("---")
    
    if not st.session_state.confirm_delete:
        if st.button("🗑️ Burn Scrolls"):
            st.session_state.confirm_delete = True
            st.rerun()
        if st.button("🧹 New Chat"):
            if len(st.session_state.messages) > 1:
                save_current_chat(st.session_state.messages, st.session_state.session_id, st.session_state.profile)
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
    else:
        st.warning(f"⚠️ Confirm? This deletes ONLY {current_user}'s history.")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("🔥 YES"):
                delete_user_history(current_user)
                st.toast(f"{current_user}'s scrolls burned!")
                st.session_state.confirm_delete = False
                st.session_state.messages = []
                st.session_state.session_id = str(uuid.uuid4())
                st.rerun()
        with col_no:
            if st.button("Cancel"):
                st.session_state.confirm_delete = False
                st.rerun()

# 9. MAIN UI
st.title("🐈‍⬛ Midnight the Mentor")

c_hope, c_rose, c_space = st.columns([1, 1, 5])

with c_hope:
    if st.button("🦄 Hope (Age 6)"):
        st.session_state.profile = "Hope"
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

with c_rose:
    # UPDATED ICON TO ROSE
    if st.button("🌹 Rose (Age 11)"):
        st.session_state.profile = "Rose"
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# 10. PROFILE LOGIC
if st.session_state.profile == "Hope":