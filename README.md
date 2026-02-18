# 🔍 Nexus Analyzer — Telegram Sentiment Analysis Dashboard

A local-first, privacy-respecting tool that connects to your Telegram account and performs deep **sentiment analysis**, **intent classification**, and **urgency detection** on your conversations — all visualized in a premium web dashboard.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Sentiment Analysis** | VADER-powered scoring (Positive / Neutral / Negative) per message |
| 🎯 **Intent Classification** | Semantic matching using `sentence-transformers` (Agreement, Urgency, Disinterest, etc.) |
| ⚡ **Urgency Detection** | Heuristic scoring based on keywords, punctuation, and response timing |
| 📈 **Emotional Drift** | Line chart visualizing sentiment and urgency trends over time |
| 💬 **Conversation Log** | Styled message stream with per-message tone indicators |
| 🔒 **Local & Private** | All data stored in a local SQLite database. Nothing leaves your machine. |

---

## 🖥️ Dashboard Preview

The dashboard features a **"Deep Space"** glassmorphism theme with:
- **Summary Cards** — Average Sentiment, Urgency Level, and Message Count
- **Gradient Charts** — Emotional Drift (Urgency in Rose, Sentiment in Emerald)
- **Message Bubbles** — Tone indicators and high-urgency alerts per message

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A Telegram account with API credentials from [my.telegram.org](https://my.telegram.org)

### 1. Clone & Setup

```powershell
# Navigate to the project directory
cd telegram_analyzer

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `telegram_analyzer` directory:

```env
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
```

> **Where to get these?**
> 1. Go to [https://my.telegram.org](https://my.telegram.org)
> 2. Log in with your phone number
> 3. Click **"API development tools"**
> 4. Create a new application to get your `api_id` and `api_hash`

### 3. Run the Server

```powershell
python main.py
```

The server will start at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🔐 Login Flow

1. Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.
2. Enter your phone number in **international format** (e.g., `+91XXXXXXXXXX`).
3. Enter the **OTP** you receive in Telegram.
4. If you have **2FA** enabled, enter your password.

---

## 📊 Using the Dashboard

1. Click **"Sync Conversations"** in the sidebar to fetch your recent chats.
2. Select any chat from the list.
3. The dashboard will automatically analyze the messages and display:
   - **Sentiment Score** (average positivity)
   - **Urgency Level**
   - **Emotional Drift Chart**
   - **Per-message tone indicators**

---

## 🗂️ Project Structure

```
telegram_analyzer/
├── api/
│   └── server.py          # FastAPI routes & analysis logic
├── core/
│   ├── analyzer.py        # Sentiment, Intent & Urgency analysis engine
│   ├── database.py        # SQLAlchemy database manager
│   ├── models.py          # ORM models (Chat, Message, Analysis)
│   └── telegram_client.py # Telethon client wrapper
├── web/
│   ├── static/
│   │   └── app.js         # Frontend logic & Chart.js rendering
│   └── templates/
│       └── index.html     # Dashboard HTML (Glassmorphism UI)
├── config.py              # Configuration loader
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
└── .env                   # Your API credentials (not committed)
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `telethon` | Telegram client library |
| `fastapi` + `uvicorn` | Web server & API framework |
| `sentence-transformers` | Semantic intent classification |
| `vaderSentiment` | Rule-based sentiment analysis |
| `sqlalchemy` | ORM for SQLite database |
| `jinja2` | HTML templating |
| `python-dotenv` | `.env` file loading |

---

## 🛡️ Privacy & Security

- **No data is sent to any external server.** All analysis runs locally.
- Your Telegram session is stored in a local `.session` file.
- The SQLite database (`telegram_analysis.db`) is stored locally.
- **Never commit your `.env` file or `.session` files to version control.**

---

## 🐛 Troubleshooting

| Issue | Solution |
|---|---|
| "Connection Refused" | Make sure `python main.py` is running |
| Login fails | Double-check `API_ID` and `API_HASH` in `.env` |
| No chats appear | Click "Sync Conversations" and wait a few seconds |
| Scores show as 0 | Try re-syncing the chat after selecting it |

---

## 📄 License

This project is for personal/educational use. Use responsibly and in accordance with [Telegram's Terms of Service](https://telegram.org/tos).
