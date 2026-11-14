import tomllib

from google import genai

key = tomllib.load(open(".streamlit/secrets.toml", "rb"))["GEMINI_API_KEY"]
client = genai.Client(api_key=key)

for model in ["gemini-3.5-flash-lite"]:
    try:
        reply = client.models.generate_content(model=model, contents="Say hello in three words")
        print(model, "-> OK:", reply.text.strip())
    except Exception as e:
        print(model, "-> FAILED:", type(e).__name__, str(e)[:160])