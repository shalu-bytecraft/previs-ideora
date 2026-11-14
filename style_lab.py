"""Feature 3: Style Lab. The same idea explored in three painting styles, side by side."""
import html
import json
import random
import re

import streamlit as st

from ai import ask_gemini

STYLES = [
    "Watercolour", "Oil painting", "Pixel art", "Ink and line", "Gouache",
    "Crayon and pastel", "Cel-shaded animation", "Charcoal sketch",
    "Paper-cut collage", "Digital matte painting",
]
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _chips(palette, size=28):
    out = ""
    for c in palette:
        hx = str(c.get("hex", "")).strip()
        if HEX.match(hx):
            out += (
                f'<span title="{hx.upper()}" style="display:inline-block;width:{size}px;height:{size}px;'
                f'border-radius:50%;background:{hx};margin:0 6px 6px 0;'
                f'border:1px solid rgba(92,74,63,.25)"></span>'
            )
    return out


def style_lab_page(label, name, desc):
    st.markdown(f"<div class='panel'><h3>{name}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    st.caption(
        "Style Lab gives you a guide and a copy-ready prompt for each style. "
        "Paste a prompt into any image tool you like."
    )

    idea = st.text_area(
        "Describe your idea",
        value=st.session_state.get("concept_idea", ""),
        key="lab_idea",
        placeholder="Example: a fox reading a map under a lantern",
        height=100,
    )
    picks = st.multiselect(
        "Choose 2 or 3 styles to compare",
        STYLES,
        default=["Watercolour", "Oil painting", "Pixel art"],
        max_selections=3,
        key="lab_styles",
    )

    if st.button("Compare Styles", key="lab_go"):
        if not idea.strip():
            st.warning("Please describe your idea first.")
        elif len(picks) < 2:
            st.warning("Please choose at least 2 styles.")
        else:
            prompt = f"""
You are an art mentor helping an artist choose a style. Support their choice, never make it for them.
Idea: {idea}
Styles to compare: {", ".join(picks)}

Return ONLY valid JSON in exactly this shape, with one item per style in the same order:
{{
  "styles": [
    {{
      "style": "Style name",
      "look": "1 or 2 sentences on how this idea would look in this style",
      "palette": [{{"hex": "#RRGGBB"}}, {{"hex": "#RRGGBB"}}, {{"hex": "#RRGGBB"}}, {{"hex": "#RRGGBB"}}],
      "technique": "1 or 2 sentences of practical tips: tools, brushes or methods",
      "best_for": "One short line on what this style suits",
      "prompt": "A detailed, copy-ready image generation prompt for this idea in this style"
    }}
  ]
}}
Do not name living artists or copyrighted characters. Variation: {random.randint(1, 10**6)}
"""
            with st.spinner("Painting your options..."):
                try:
                    raw = ask_gemini(prompt).strip()
                    raw = raw[raw.find("{"): raw.rfind("}") + 1]
                    data = json.loads(raw)
                    items = [s for s in data.get("styles", []) if s.get("prompt")]
                    if len(items) < 2:
                        raise ValueError("Not enough styles came back. Please try again.")
                    st.session_state.lab_data = {"items": items[:3], "idea": idea}
                    st.session_state.lab_version = st.session_state.get("lab_version", 0) + 1
                except Exception as e:
                    st.warning("Gemini could not finish this one.")
                    st.code(f"{type(e).__name__}: {str(e)[:300]}")

    if "lab_data" in st.session_state:
        items = st.session_state.lab_data["items"]
        version = st.session_state.get("lab_version", 0)

        st.divider()
        label("brush", "Your Style Options", "h2")

        # compact side-by-side look at the three palettes
        strip = st.columns(len(items))
        for col, s in zip(strip, items):
            with col:
                st.markdown(f"**{html.escape(str(s.get('style', 'Style')))}**")
                st.markdown(_chips(s.get("palette", []), 22), unsafe_allow_html=True)

        # full details, one readable card per style
        for i, s in enumerate(items):
            with st.container(border=True):
                label("sparkle", html.escape(str(s.get("style", "Style"))))
                left, right = st.columns(2)
                with left:
                    st.markdown(str(s.get("look", "")))
                    st.markdown(_chips(s.get("palette", [])), unsafe_allow_html=True)
                    st.markdown(f"**Best for:** {s.get('best_for', '')}")
                with right:
                    st.markdown(f"**Technique:** {s.get('technique', '')}")
                    st.text_area(
                        "Image prompt (edit and copy)",
                        value=str(s.get("prompt", "")),
                        key=f"lab_prompt_{version}_{i}",
                        height=150,
                    )

        names = [str(s.get("style", f"Style {i + 1}")) for i, s in enumerate(items)]
        st.radio("Which style are you going with?", names, horizontal=True, key=f"lab_pick_{version}")
        st.session_state.chosen_style = st.session_state.get(f"lab_pick_{version}", names[0])

        sheet = "PREVIS-IDEORA STYLE LAB\nIdea: " + st.session_state.lab_data["idea"] + "\n\n"
        for i, s in enumerate(items):
            sheet += (
                f"{s.get('style', '')}\nLook: {s.get('look', '')}\n"
                f"Palette: {', '.join(str(c.get('hex', '')).upper() for c in s.get('palette', []))}\n"
                f"Technique: {s.get('technique', '')}\nBest for: {s.get('best_for', '')}\n"
                f"Prompt: {st.session_state.get(f'lab_prompt_{version}_{i}', s.get('prompt', ''))}\n\n"
            )
        st.download_button("Download Style Guide", data=sheet, file_name="previs_ideora_styles.txt", mime="text/plain")