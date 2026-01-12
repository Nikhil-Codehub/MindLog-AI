import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# --- PATH FIX ---
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from src.database import init_db, add_entry, get_recent_entries, get_all_dates, get_entries_by_date
    from src.model_ai import MoodAnalyzer
    from src.chatbot import get_chat_response
except ModuleNotFoundError:
    from database import init_db, add_entry, get_recent_entries, get_all_dates, get_entries_by_date
    from model_ai import MoodAnalyzer
    from chatbot import get_chat_response

# 1. Page Config
st.set_page_config(page_title="MindLog AI", layout="wide")
init_db()

@st.cache_resource
def load_model():
    return MoodAnalyzer()

analyzer = load_model()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🧠 MindLog")
app_mode = st.sidebar.radio("Go to:", ["✍️ Write Diary", "📅 Past History"])

# --- MODE 1: WRITE DIARY (Purana Chat Interface) ---
if app_mode == "✍️ Write Diary":
    
    # --- Sidebar Graph Logic ---
    st.sidebar.divider()
    st.sidebar.write("### Mood Trends")
    history_data = get_recent_entries(limit=14)
    if history_data:
        df = pd.DataFrame(history_data, columns=["Time", "Risk Score"])
        avg_score = df["Risk Score"].mean()
        if avg_score > 0.7:
            st.sidebar.error("⚠️ Status: High Risk")
        elif avg_score > 0.4:
            st.sidebar.warning("⚠️ Status: Elevated Stress")
        else:
            st.sidebar.success("✅ Status: Stable")
        
        fig = px.line(df, x="Time", y="Risk Score", markers=True, title="Recent Trend")
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
        st.sidebar.plotly_chart(fig)

    # --- Main Chat UI ---
    st.title("📖 MindLog: Today's Entry")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("How are you feeling right now?")

    if user_input:
        # 1. User Message Dikhayein
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # 2. Analyze & Generate
        risk_score, label = analyzer.analyze_text(user_input)
        
        with st.spinner("MindLog is thinking..."):
            bot_reply = get_chat_response(user_input)

        # 3. Bot Message Dikhayein
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.write(bot_reply)
        
        # 4. Save COMPLETE Chat to DB (User + Bot)
        add_entry(user_input, bot_reply, risk_score, label)

# --- MODE 2: PAST HISTORY (Naya Feature) ---
elif app_mode == "📅 Past History":
    st.title("📅 Your Journey")
    
    # 1. Dates Fetch karo
    all_dates = get_all_dates()
    
    if not all_dates:
        st.info("No entries found yet. Start writing in the 'Write Diary' tab!")
    else:
        # 2. Date Selector
        selected_date = st.selectbox("Select a Date to view:", all_dates)
        
        # 3. Us date ka data lao
        day_entries = get_entries_by_date(selected_date)
        
        st.divider()
        st.subheader(f"History for {selected_date}")
        
        # 4. Chat Format me Display karo
        for time, user_text, bot_text, label, score in day_entries:
            # Time formatting (14:30:00 -> 02:30 PM)
            time_obj = pd.to_datetime(time)
            nice_time = time_obj.strftime("%I:%M %p")
            
            # --- Chat Bubble Design ---
            with st.chat_message("user"):
                st.write(f"**You** ({nice_time})")
                st.write(user_text)
                # Mood Badge
                if score > 0.6:
                    st.caption(f"⚠️ Detected Mood: {label} (Risk: {score:.2f})")
                else:
                    st.caption(f"✅ Detected Mood: {label}")
            
            with st.chat_message("assistant"):
                st.write("**MindLog AI**")
                st.write(bot_text)
            
            st.divider() # Line separator between entries