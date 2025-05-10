# AI Sentiment Scanner

A powerful tool for analyzing Google Play Store reviews using AI to provide deep insights into user feedback and sentiment trends.

## Features

### Single Period Analysis
- Analyze reviews for a specific time period
- Get AI-powered insights on user sentiment and feedback
- View key metrics including:
  - Total reviews
  - Average sentiment
  - Average rating
  - Response rate
- Track sentiment trends over time
- Identify recurring topics and themes
- View raw review data

### Period Comparison
- Compare reviews across two different time periods
- Analyze changes in user sentiment and feedback
- View side-by-side metrics for both periods
- Get AI-powered analysis of changes and trends
- Track improvements or emerging issues
- Compare theme distributions

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key in `core/settings.py`
4. Run the application:
   ```bash
   streamlit run app/main.py
   ```

## Usage

1. Select an app from the dropdown or enter a custom Google Play Store URL
2. Choose your analysis mode:
   - Single Period: Analyze reviews for one time period
   - Period Comparison: Compare reviews across two time periods
3. Select your date range(s)
4. Click "Analyze App" to start the analysis
5. View the results:
   - Key metrics and statistics
   - AI-powered insights
   - Sentiment trends
   - Theme distribution
   - Raw review data

## Technical Details

- Built with Streamlit for the user interface
- Uses OpenAI's GPT-3.5 Turbo for AI analysis
- Implements caching for efficient data retrieval
- Processes up to 200 reviews per analysis
- Supports custom date ranges for flexible analysis

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for Google Play Store access

## Contributing

Feel free to submit issues and enhancement requests!

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

© 2025 AI Sentiment Scanner. Built with 🧠 and ☕.