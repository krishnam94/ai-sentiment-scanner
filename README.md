# 📱 AI Sentiment Scanner

**AI Sentiment Scanner** is a Streamlit-based tool for analyzing and comparing customer sentiment from **Google Play Store reviews**. It helps track public perception, identify pain points, and monitor how user sentiment evolves over time.

---

## 🔧 Features

- 📥 Fetches reviews from Google Play for apps like Singtel, StarHub, M1, and TPG
- 📈 Sentiment analysis using TextBlob
- 🧠 GPT-4 powered summaries of review themes (clustered for cost-efficiency)
- 📦 Daily snapshot storage of fetched reviews for historical tracking
- ♻️ Caching to avoid repeated LLM calls
- 🧪 Compare two apps side-by-side
- 💻 Streamlit-based interactive UI

---

## 📂 Project Structure

```
ai-sentiment-scanner/
├── app/                     # Streamlit frontend
│   └── main.py              # UI logic and review comparison
├── core/                    # Core processing modules
│   ├── review_fetcher.py    # Pulls Play Store reviews
│   ├── analyzer.py          # Sentiment & date normalization
│   ├── summarizer.py        # GPT-based clustering + summarization
│   └── utils.py             # Caching, snapshot storage
├── config/                  # Configuration files
│   └── settings.py          # API keys (loaded via .env)
├── data/
│   ├── snapshots/           # Daily saved review JSONs
│   └── summaries/           # Cached GPT summaries
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourname/ai-sentiment-scanner.git
cd ai-sentiment-scanner
```

### 2. Set up environment variables
Create a `.env` file:
```env
OPENAI_API_KEY=your_api_key_here
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the app
```bash
streamlit run app/main.py
```

---

## 🧠 Ideal Use Cases

- Product teams tracking app feedback trends
- Competitive benchmarking
- Sentiment-driven UX research

---

## 🛠 Roadmap

- [ ] Add App Store (iOS) support
- [ ] Enable PDF/CSV report exports
- [ ] Weekly trend summarizer dashboard

---

## 📬 Feedback & Contributions
Open to ideas, improvements, or collaborations! Submit an issue or reach out directly.

---

© 2025 AI Sentiment Scanner. Built with 🧠 and ☕.