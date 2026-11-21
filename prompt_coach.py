"""Feature 9: Prompt Coach. Suggests better image prompts for the chosen style and mood."""
import json
import random

import streamlit as st

from ai import ask_gemini


def _bullets(items):
    return "\n".join(f"- {str(i)}" for i in items if str(i).strip())


def prompt_coach_page(label, name, desc):
    st.markdown(f"<div class='panel'><h3>{name}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    st.caption("Paste a prompt you already use. The coach shows what works, what is missing, and a stronger version you can edit.")

    start = (st.session_state.get("concept_data") or {}).get("image_prompt", "")
    text = st.text_area(
        "Your image prompt",
        value=start,
        key="pc_in",
        height=140,
        placeholder="Example: a fox reading a map under a lantern",
    )
    style = st.text_input(
        "Art style (optional)",
        value=st.session_state.get("chosen_style", ""),
        key="pc_style",
        placeholder="Example: watercolour",
    )
    mood = st.text_input("Mood (optional)", key="pc_mood", placeholder="Example: calm, dreamy, golden hour")

    if st.button("Coach My Prompt", key="pc_go"):
        if not text.strip():
            st.warning("Please paste a prompt first.")
        else:
            extra = ""
            if style.strip():
                extra += f"Chosen art style: {style}. "
            if mood.strip():
                extra += f"Wanted mood: {mood}. "
            prompt = f"""
You are a friendly prompt coach for artists. Keep the artist's own idea. Never replace it.
Their prompt: {text}
{extra}

Return ONLY valid JSON in exactly this shape:
{{
  "working": ["2 or 3 things that already work well"],
  "missing": ["2 or 3 things that are missing or vague"],
  "improved": "A stronger, detailed, copy-ready version of their prompt",
  "variations": [
    {{"label": "Short name for this twist", "prompt": "A different take on the same idea"}},
    {{"label": "Short name for this twist", "prompt": "Another different take on the same idea"}}
  ],
  "tip": "One short practical tip"
}}
Do not name living artists or copyrighted characters. Variation: {random.randint(1, 10**6)}
"""
            with st.spinner("Reading your prompt..."):
                try:
                    raw = ask_gemini(prompt).strip()
                    raw = raw[raw.find("{"): raw.rfind("}") + 1]
                    data = json.loads(raw)
                    if not data.get("improved"):
                        raise ValueError("No improved prompt came back. Please try again.")
                    st.session_state.pc_data = {
                        "working": data.get("working", []),
                        "missing": data.get("missing", []),
                        "improved": str(data.get("improved", "")),
                        "variations": [v for v in data.get("variations", []) if v.get("prompt")][:2],
                        "tip": str(data.get("tip", "")),
                        "original": text,
                    }
                    st.session_state.pc_version = st.session_state.get("pc_version", 0) + 1
                except Exception as e:
                    st.warning("Gemini could not finish this one.")
                    st.code(f"{type(e).__name__}: {str(e)[:300]}")

    if "pc_data" in st.session_state:
        d = st.session_state.pc_data
        version = st.session_state.get("pc_version", 0)

        st.divider()
        label("brush", "Your Coach Notes", "h2")

        left, right = st.columns(2)
        with left:
            with st.container(border=True):
                label("tree", "What is working")
                st.markdown(_bullets(d["working"]))
        with right:
            with st.container(border=True):
                label("moon", "What is missing")
                st.markdown(_bullets(d["missing"]))

        with st.container(border=True):
            label("sparkle", "Stronger prompt")
            improved = st.text_area(
                "Improved prompt (edit and copy)",
                value=d["improved"],
                key=f"prompt_coach_improved_{version}",
                height=150,
            )

        sheet = f"PREVIS-IDEORA PROMPT COACH\n\nORIGINAL\n{d['original']}\n\nIMPROVED\n{improved}\n"
        for i, v in enumerate(d["variations"]):
            with st.container(border=True):
                label("palette", str(v.get("label", f"Variation {i + 1}")).replace("<", "").replace(">", ""))
                vt = st.text_area(
                    "Variation prompt (edit and copy)",
                    value=str(v.get("prompt", "")),
                    key=f"prompt_coach_var_{version}_{i}",
                    height=120,
                )
            sheet += f"\nVARIATION {i + 1}: {v.get('label', '')}\n{vt}\n"

        if d["tip"]:
            st.caption(f"Tip: {d['tip']}")
        st.download_button("Download Coach Notes", data=sheet, file_name="previs_ideora_prompt_coach.txt", mime="text/plain")
