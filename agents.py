import os
import time
import re
from pathlib import Path
from dotenv import load_dotenv
import google.genai as genai
from tools import web_search, scrape_url

_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)


def get_llm_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GOOGLE_GENAI_API_KEY")
        except Exception:
            pass
            
    if not api_key:
        raise EnvironmentError(
            "Missing GOOGLE_GENAI_API_KEY. Set it in .env, Streamlit Secrets, or environment variables before running."
        )
    return genai.Client(api_key=api_key)


def _extract_response_text(response: genai.types.GenerateContentResponse) -> str:
    if response is None:
        return ""
    text = getattr(response, "text", None)
    if text:
        return text.strip()
    if response.candidates:
        candidate = response.candidates[0]
        if candidate and candidate.content and candidate.content.parts:
            collected = []
            for part in candidate.content.parts:
                if getattr(part, "text", None):
                    collected.append(part.text)
            return "".join(collected).strip()
    return str(response)


def _send_prompt(prompt: str, model: str = "gemini-2.5-flash") -> str:
    client = get_llm_client()
    last_error = None
    for attempt in range(3):
        try:
            chat = client.chats.create(model=model)
            response = chat.send_message(prompt)
            return _extract_response_text(response)
        except Exception as e:
            last_error = e
            # If it's a 503 or 429 error, wait and retry
            if "503" in str(e) or "429" in str(e):
                time.sleep(2 * (attempt + 1))
                continue
            raise e
    raise last_error


class SimpleAgent:
    def __init__(self, tool, no_url_message: str):
        self.tool = tool
        self.no_url_message = no_url_message

    def invoke(self, prompt: str) -> str:
        query = prompt.strip()
        if self.tool is web_search:
            return self.tool(query)
        url = self._extract_url(prompt)
        if not url:
            return self.no_url_message
        return self.tool(url)

    def _extract_url(self, text: str) -> str | None:
        url_match = re.search(r"https?://[^\s,;]+", text)
        if url_match:
            return url_match.group(0).rstrip(".,;\n")
        url_match = re.search(r"URL:\s*(\S+)", text)
        if url_match:
            return url_match.group(1).rstrip(".,;\n")
        return None


class SimpleChain:
    def __init__(self, prompt_template: str):
        self.prompt_template = prompt_template

    def invoke(self, inputs: dict) -> str:
        prompt = self.prompt_template.format(**inputs)
        return _send_prompt(prompt)


def build_search_agent():
    return SimpleAgent(web_search, "Could not find a URL from the search results.")


def build_reader_agent():
    return SimpleAgent(scrape_url, "Could not extract a URL to scrape from the search results.")


writer_prompt = (
    "You are an expert research writer. Write clear, structured and insightful reports.\n\n"
    "Write a detailed research report on the topic below.\n\n"
    "Topic: {topic}\n\n"
    "Research Gathered:\n{research}\n\n"
    "Structure the report as:\n- Introduction\n- Key Findings (minimum 3 well-explained points)\n- Conclusion\n- Sources (list all URLs found in the research)\n\n"
    "Be detailed, factual and professional."
)


def build_writer_chain():
    return SimpleChain(writer_prompt)


critic_prompt = (
    "You are a sharp and constructive research critic. Be honest and specific.\n\n"
    "Review the research report below and evaluate it strictly.\n\n"
    "Report:\n{report}\n\n"
    "Respond in this exact format:\n\n"
    "Score: X/10\n\n"
    "Strengths:\n- ...\n- ...\n\n"
    "Areas to Improve:\n- ...\n- ...\n\n"
    "One line verdict:\n..."
)


def build_critic_chain():
    return SimpleChain(critic_prompt)

