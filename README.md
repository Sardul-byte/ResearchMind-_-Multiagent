# ResearchMind · Multi-Agent Research System

ResearchMind is a professional, Streamlit-based research assistant that combines multi-agent automation with web search, content extraction, report generation, and quality critique.

## Key Features

- **Automated Research Pipeline:** Search, scrape, write, and critique using specialized agent stages.
- **Streamlit Interface:** Clean, responsive dashboard for input, progress tracking, and results.
- **Gemini + Tavily Integration:** Uses Google Generative Language API for writing and Tavily for search.
- **Secure Configuration:** Sensitive credentials are stored locally in `.env` and excluded from Git.

## Technology Stack

- Python 3.10+
- Streamlit
- google-genai
- tavily-python
- BeautifulSoup
- requests

## Installation

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

3. Create a `.env` file in the project root and add your API keys:
   ```text
   GOOGLE_GENAI_API_KEY=your-google-genai-api-key
   TAVILY_API_KEY=your-tavily-api-key
   ```

## Usage

Run the app with Streamlit:

```powershell
python -m streamlit run app.py
```

Then open the browser at:

```text
http://localhost:8501
```

## Deployment

This project is ready to deploy on platforms that support Streamlit apps. Keep the `.env` file local and use environment variables in your deployment platform for API keys.

Live demo: [ResearchMind · AI Research Agent · Streamlit](https://researchmind--multiagent-kb2iju3snceeiyadkryrka.streamlit.app/)

## Notes

- `.env` is included in `.gitignore` to protect secrets.
- Ensure the Google Generative Language API and Tavily API keys are valid before running.
- If the application fails to start, verify that the `.env` file exists and the keys are correct.

## Repository

Remote: `https://github.com/Sardul-byte/ResearchMind-_-Multiagent.git`
