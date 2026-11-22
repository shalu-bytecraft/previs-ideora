import json
import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def _client() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def init_db():
    try:
        _client()
    except Exception:
        pass


def register_user(email: str, password: str):
    email = email.strip().lower()
    if not email or "@" not in email:
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    try:
        res = _client().auth.sign_up({"email": email, "password": password})
        if res.user:
            return True, "Account created!"
        return False, "Could not create account."
    except Exception as e:
        return False, str(e)


def login_user(email: str, password: str):
    email = email.strip().lower()
    if not email or not password:
        return False, "Please enter both email and password."
    try:
        res = _client().auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            return True, res.user.email
        return False, "Invalid email or password."
    except Exception:
        return False, "Invalid email or password."


def save_item(user_email: str, category: str, title: str, content):
    if isinstance(content, str):
        try:
            payload = json.loads(content)
        except Exception:
            payload = {"text": content}
    else:
        payload = content

    _client().table("projects").insert({
        "user_email": user_email.strip().lower(),
        "category": category,
        "title": title.strip() or "Untitled",
        "payload": payload,
    }).execute()


def get_items(user_email: str, category: str = None):
    query = (
        _client()
        .table("projects")
        .select("id, category, title, payload, created_at")
        .eq("user_email", user_email.strip().lower())
        .order("created_at", desc=True)
    )
    if category and category != "All":
        query = query.eq("category", category)
    res = query.execute()

    out = []
    for r in res.data or []:
        content_str = json.dumps(r.get("payload") or {})
        created = str(r.get("created_at", ""))[:16].replace("T", " ")
        out.append((r["id"], r["category"], r["title"], content_str, created))
    return out


def delete_item(item_id):
    _client().table("projects").delete().eq("id", item_id).execute()