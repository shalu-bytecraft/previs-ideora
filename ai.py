import os
import time

import streamlit as st
from google import genai
from google.genai import errors

# Tried in order. 2.5 models are no longer available to new accounts.
MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]


def get_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY")


@st.cache_data(show_spinner=False, ttl=3600)
def ask_gemini(prompt: str) -> str:
    client = genai.Client(api_key=get_key())
    last = None
    for model in MODELS:
        for attempt in range(2):
            try:
                reply = client.models.generate_content(model=model, contents=prompt)
                return reply.text
            except errors.APIError as e:
                last = e
                if e.code == 404:
                    break  # model not available, try the next one
                if e.code in (429, 500, 503, 504):
                    time.sleep(2 ** attempt)
                    continue
                raise
    raise RuntimeError("Gemini is busy") from last