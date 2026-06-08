# ResearchMind · Multi-Agent Research System

A Streamlit-powered AI research assistant that uses web search, content scraping, automated report writing, and critique feedback.

## Setup

1. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
3. Configure environment keys in `.env`:
   ```text
   GOOGLE_GENAI_API_KEY=your-google-genai-api-key
   TAVILY_API_KEY=your-tavily-api-key
   ```

## Run

```powershell
python -m streamlit run app.py
```

## Notes

- `.env` is ignored by Git to keep API keys private.
- Use valid Google Generative Language and Tavily keys before running.
- If the app fails, verify `.env` is present and contains correct keys.
