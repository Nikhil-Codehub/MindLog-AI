import sqlite3
from datetime import datetime

DB_NAME = "mindlog.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Updated Schema: Ab 'bot_text' bhi save hoga
    c.execute('''CREATE TABLE IF NOT EXISTS diary_entries
                 (id INTEGER PRIMARY KEY, 
                  timestamp TEXT, 
                  user_text TEXT, 
                  bot_text TEXT,
                  depression_score REAL,
                  label TEXT)''')
    conn.commit()
    conn.close()

def add_entry(user_text, bot_text, score, label):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO diary_entries (timestamp, user_text, bot_text, depression_score, label) VALUES (?, ?, ?, ?, ?)",
              (timestamp, user_text, bot_text, score, label))
    conn.commit()
    conn.close()

def get_recent_entries(limit=10):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT timestamp, depression_score FROM diary_entries ORDER BY id DESC LIMIT ?", (limit,))
    data = c.fetchall()
    conn.close()
    return data[::-1]

# --- History Feature Functions ---

def get_all_dates():
    """Database se saari unique dates nikalta hai"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Timestamp string (YYYY-MM-DD HH:MM:SS) me se pehle 10 chars (Date) nikal rahe hain
    c.execute("SELECT DISTINCT SUBSTR(timestamp, 1, 10) FROM diary_entries ORDER BY timestamp DESC")
    dates = [row[0] for row in c.fetchall()]
    conn.close()
    return dates

def get_entries_by_date(date_str):
    """Specific date ki saari chats lata hai"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Us date se match hone wali entries dhundo
    c.execute("SELECT timestamp, user_text, bot_text, label, depression_score FROM diary_entries WHERE timestamp LIKE ?", (f"{date_str}%",))
    data = c.fetchall()
    conn.close()
    return data