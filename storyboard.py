"""Feature 4: Storyboard Builder. A shot list with shot type, camera angle, action and mood."""
import html
import json
import random

import streamlit as st

from ai import ask_gemini


def _frame(shot_type):
    t = str(shot_type).lower()
    if any(w in t for w in ("wide", "establishing", "long", "aerial", "full")):
        return "wide"
    if any(w in t for w in ("close", "detail", "insert")):
        return "close"
    return "medium"


def storyboard_page(label, name, desc):
    st.markdown(f"<div class='panel'><h3>{name}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    st.caption("You get a shot list with a prompt for every panel. Paste the prompts into any image tool.")

    idea = st.text_area(
        "Describe your story or scene",
        value=st.session_state.get("concept_idea", ""),
        key="sb_idea",
        placeholder="Example: a lighthouse keeper finds a message in a bottle",
        height=100,
    )
    style = st.text_input(
        "Art style (optional)",
        value=st.session_state.get("chosen_style", ""),
        key="sb_style",
        placeholder="Example: watercolour",
    )
    count = st.slider("How many shots?", 3, 8, 6, key="sb_n")

    if st.button("Build Storyboard", key="sb_go"):
        if not idea.strip():
            st.warning("Please describe your story or scene first.")
        else:
            style_line = f"Art style for the image prompts: {style}." if style.strip() else ""
            prompt = f"""
You are a storyboard artist's assistant. Support the artist, never replace their vision.
Story or scene: {idea}
{style_line}

Plan exactly {count} shots with a clear beginning, middle and end.
Return ONLY valid JSON in exactly this shape:
{{
  "title": "Short storyboard title",
  "shots": [
    {{
      "shot_type": "Wide, Medium, Close-up, Extreme close-up, Over-the-shoulder or Aerial",
      "camera_angle": "Eye level, Low angle, High angle, Bird's-eye or Dutch tilt",
      "action": "What happens in this shot, 1 or 2 sentences",
      "mood": "A few words on mood and lighting",
      "image_prompt": "A detailed, copy-ready image prompt for this panel"
    }}
  ]
}}
Do not name living artists or copyrighted characters. Variation: {random.randint(1, 10**6)}
"""
            with st.spinner("Planning your shots..."):
                try:
                    raw = ask_gemini(prompt).strip()
                    raw = raw[raw.find("{"): raw.rfind("}") + 1]
                    data = json.loads(raw)
                    shots = [s for s in data.get("shots", []) if s.get("action")]
                    if len(shots) < 2:
                        raise ValueError("Not enough shots came back. Please try again.")
                    st.session_state.sb_data = {
                        "title": str(data.get("title", "Storyboard")),
                        "shots": shots,
                        "idea": idea,
                    }
                    st.session_state.sb_version = st.session_state.get("sb_version", 0) + 1
                except Exception as e:
                    st.warning("Gemini could not finish this one.")
                    st.code(f"{type(e).__name__}: {str(e)[:300]}")

    if "sb_data" in st.session_state:
        sb = st.session_state.sb_data
        version = st.session_state.get("sb_version", 0)

        st.divider()
        label("book", html.escape(sb["title"]), "h2")

        PER_ROW = 3
        shots = sb["shots"]
        for start in range(0, len(shots), PER_ROW):
            cols = st.columns(PER_ROW)
            for j, col in enumerate(cols):
                i = start + j
                if i >= len(shots):
                    break
                s = shots[i]
                with col:
                    with st.container(border=True, key=f"shotcard_{i}"):
                        label("sparkle", f"Shot {i + 1}", "h4")
                        st.markdown(
                            f'<img src="/app/static/frames/{_frame(s.get("shot_type", ""))}.svg" '
                            f'alt="framing sketch" style="width:65%;display:block;margin:0 auto">',
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"**{s.get('shot_type', '')}** · {s.get('camera_angle', '')}")
                        st.markdown(str(s.get("action", "")))
                        with st.expander("Mood & prompt"):
                            st.markdown(f"**Mood:** {s.get('mood', '')}")
                            st.text_area(
                                "Panel prompt (edit and copy)",
                                value=str(s.get("image_prompt", "")),
                                key=f"sb_prompt_{version}_{i}",
                                height=120,
                            )

        

        sheet = f"PREVIS-IDEORA STORYBOARD\n{sb['title']}\nIdea: {sb['idea']}\n\n"
        for i, s in enumerate(sb["shots"]):
            sheet += (
                f"SHOT {i + 1}: {s.get('shot_type', '')}, {s.get('camera_angle', '')}\n"
                f"Action: {s.get('action', '')}\nMood: {s.get('mood', '')}\n"
                f"Prompt: {st.session_state.get(f'sb_prompt_{version}_{i}', s.get('image_prompt', ''))}\n\n"
            )
        st.download_button("Download Shot List", data=sheet, file_name="previs_ideora_storyboard.txt", mime="text/plain")
