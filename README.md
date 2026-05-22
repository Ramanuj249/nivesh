# 📈 NIVESH — AI-Powered Indian Stock Research Analyst

> Your personal AI equity research analyst for the Indian stock market.

NIVESH is a multi-agent AI system that performs end-to-end stock research on any NSE/BSE listed company — just like a SEBI-registered research analyst — and delivers a professional research report in seconds.

---

## 🚀 Features

- **Fundamental Analysis** — revenue, profit, debt, ROE, ROCE
- **Technical Analysis** — moving averages, RSI, MACD, support/resistance
- **News & Sentiment** — latest news with AI sentiment scoring
- **Peer Comparison** — how the stock stacks up against competitors
- **BUY / HOLD / SELL** recommendation with reasoning
- **Telegram Bot** — daily alerts, quick price checks, morning digest
- **Real-time Data** — live NSE/BSE data via yfinance

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq (llama-3.1-8b-instant) |
| Agent Framework | LangGraph + LangChain |
| Stock Data | yfinance |
| News | NewsAPI + DuckDuckGo |
| Frontend | Streamlit + Plotly |
| Telegram | python-telegram-bot |

---

## 📁 Project Structure

```
nivesh/
├── app.py                  ← Streamlit entry point
├── agents/                 ← one AI agent per file
├── graph/                  ← LangGraph workflow
├── tools/                  ← data fetching tools
├── telegram_bot/           ← Telegram integration
└── utils/                  ← helpers and formatters
```

---

## ⚙️ Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/nivesh.git
cd nivesh

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API keys
cp .env.example .env
# Edit .env and add your keys

# 5. Run the app
streamlit run app.py
```

---

## 🔑 Environment Variables

```
GROQ_API_KEY=your_groq_api_key
NEWS_API_KEY=your_newsapi_key
```

---

## ⚠️ Disclaimer

NIVESH is for educational purposes only. It is not SEBI registered and does not constitute financial advice. Always do your own research before investing.

---

Built with ❤️ by Shivam