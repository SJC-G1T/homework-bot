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
    /* Main Background */
    .stApp {
        background: linear-gradient(to bottom right, #2e1a47, #0e0b16);
        color: #e0d4fc;
    }
    
    /* UNIVERSAL BUTTON STYLE - All buttons are now identical */
    .stButton > button {
        width: 100%;
        height: 60px; /* Fixed pixel height for perfect alignment */
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

    /* FIX: Don't hide the header, just make it transparent so the 'Open Sidebar' arrow stays visible */
    header {
        background: rgba(0,0,0,0) !important;
    }
    
    /* Adjust top spacing */
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
    """Only deletes the history key for the specific user"""
    data = load_all_history()
    data[user_name] = [] # Wipe only this user
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# 4. INIT STATE
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "profile" not in st.session_state:
    st.session_state.profile = "Rose" # Default to eldest
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

# 5. SIDEBAR
with st.sidebar:
    st.header("🔮 Wizard Settings")
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    api_input = st.text_input("Spell Password (API Key)", type="password", value=st.session_state.api_key)
    if api_input:
        st.session_state.api_key = api_input

    st.markdown("---")
    
    # HISTORY VIEWER
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
    
    # DELETE BUTTON LOGIC
    if not st.session_state.confirm_delete:
        if st.button("🗑️ Burn Scrolls"):
            st.session_state.confirm_delete = True
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

    # NEW CHAT BUTTON
    if not st.session_state.confirm_delete:
        if st.button("🧹 New Chat"):
            if len(st.session_state.messages) > 1:
                save_current_chat(st.session_state.messages, st.session_state.session_id, st.session_state.profile)
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

# 6. MAIN UI
st.title("🐈‍⬛ Midnight the Mentor")

# --- LEFT ALIGN FIX ---
# [1, 1, 5] means 2 small columns + 1 huge spacer column.
c_hope, c_rose, c_space = st.columns([1, 1, 5])

with c_hope:
    # Hope is now 6
    if st.button("🦄 Hope (Age 6)"):
        st.session_state.profile = "Hope"
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

with c_rose:
    # Rose is now 11
    if st.button("🦅 Rose (Age 11)"):
        st.session_state.profile = "Rose"
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# 7. PROFILE LOGIC (CORRECTED AGES)
if st.session_state.profile == "Hope":
    st.info("🦄 Mode: Hope (Magical & Fun)")
    limit = 10
    SYSTEM_PROMPT = """
    You are Midnight, a magical black cat 🐈‍⬛.
    Audience: Hope, age 6.
    Tone: Playful, hungry for snacks, uses emojis.
    Rules: Keep answers short. Use magic metaphors.
    """
else:
    st.info("🦅 Mode: Rose (Study Support & Life Coach)")
    limit = 30
    SYSTEM_PROMPT = """
    You are Midnight, a snarky but wise black cat 🐈‍⬛. 
    Audience: Rose, age 11 (Secondary School).
    Traits: Sassy, dry humor, supportive.
    MODE ACADEMIC: Socratic method. Give magical hints.
    MODE LIFE COACH: Listen to drama. Offer wise advice.
    SAFETY: Redirect dangerous topics to Dad.
    """

# Ensure System Prompt is correct
if not st.session_state.messages:
    st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})
else:
    st.session_state.messages[0]["content"] = SYSTEM_PROMPT

# 8. STOP IF NO KEY
if not st.session_state.api_key:
    st.warning("⚠️ The crystal ball is locked. Please enter the Password (API Key) in the sidebar.")
    st.stop()

client = OpenAI(api_key=st.session_state.api_key)

# 9. DISPLAY CHAT
for msg in st.session_state.messages:
    if msg["role"] != "system":
        user_avatar = "👧" if msg["role"] == "user" else "🐈‍⬛"
        with st.chat_message(msg["role"], avatar=user_avatar):
            st.markdown(msg["content"])

# 10. INPUT
prompt_placeholder = f"Ask Midnight... (Tip: Tap 🎙️ on your keyboard to speak!)"

if user_input := st.chat_input(prompt_placeholder):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👧"):
        st.markdown(user_input)

    if len(st.session_state.messages) >= limit:
        context = st.session_state.messages + [{"role": "system", "content": "Limit reached. Wrap up."}]
        st.warning("🐈‍⬛ Midnight is getting sleepy... (Limit reached)")
    else:
        context = st.session_state.messages

    with st.chat_message("assistant", avatar="🐈‍⬛"):
        stream = client.chat.completions.create(
            model="gpt-4o", messages=context, stream=True
        )
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    save_current_chat(st.session_state.messages, st.session_state.session_id, st.session_state.profile)