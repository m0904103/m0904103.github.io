# AI US Stock Trading Strategy Dashboard

A professional full-stack stock scanning and trading strategy dashboard based on FastAPI and React.

## 🚀 Architecture (Simon's Hybrid Recommendation)
- **Backend**: Python (FastAPI) - Optimized with async `yfinance` for fast scanning.
- **Frontend**: React.js (Vite + Tailwind CSS) - Premium financial dark mode UI.
- **Strategy**: Turtle Strategy (Breakouts), Day Trading (RSI/MACD), Long-term trend.
- **Charts**: TradingView Lightweight Charts integration.
- **Notifications**: Automated Telegram push for Buy/Sell signals.

## 🛠️ Local Development

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## ☁️ Deployment Guide
1. **Frontend**: Deploy to **Vercel** (connect this GitHub repo).
2. **Backend**: Deploy to **Render** or **Railway**.
3. **Env Vars**: Set `TELEGRAM_TOKEN` and `CHAT_ID` on your backend host.

## 📈 Credits
- Strategy Logic: Based on Python technical analysis.
- UI/UX Design: Financial Dark Mode.
- Deployment Strategy: Simon's Expert Tip.
