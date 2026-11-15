"""Feature 8: Sketch Guide. The artist uploads a sketch and the AI builds on it."""
import html
import json
import random
import re
from io import BytesIO

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps

from ai import ask_gemini_image
from palette import _swatches


def _prepare(file):
    img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
    img.thumbnail((1024, 1024))
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return buf.getvalue()


def _hex(value):
    v = str(value).strip()
    return v if re.fullmatch(r"#[0-9A-Fa-f]{6}", v) else "#DDD3C7"


def sketch_page(label, name, desc):
    st.markdown(f"<div class='panel'><h3>{name}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    st.caption("Upload your own drawing. The AI reads it and builds on it. It never replaces your work.")

    file = st.file_uploader(
        "Upload a sketch or reference (PNG, JPG or WEBP)",
        type=["png", "jpg", "jpeg", "webp"],
        key="sk_file",
    )
    note = st.text_input(
        "What should the AI keep or add? (optional)",
        key="sk_note",
        placeholder="Example: keep the pose, make it a rainy night",
    )
    style = st.text_input(
        "Art style (optional)",
        value=st.session_state.get("chosen_style", ""),
        key="sk_style",
        placeholder="Example: watercolour",
    )

    if file is not None:
        st.image(file, caption="Your sketch", width=240)

    if st.button("Read My Sketch", key="sk_go"):
        if file is None:
            st.warning("Please upload a sketch first.")
        else:
            note_line = f"The artist asks: {note}." if note.strip() else ""
            style_line = f"Preferred art style: {style}." if style.strip() else ""
            prompt = f"""
You are an art assistant. Look carefully at the artist's sketch.
The artist's drawing is the master: support it, never redraw over it or replace it.
{note_line}
{style_line}

Return ONLY valid JSON in exactly this shape:
{{
  "what_i_see": "Two short sentences on the subject and composition",
  "keep": ["3 or 4 short items worth preserving, such as pose, shapes or framing"],
  "palette": [
    {{"name": "Colour name", "hex": "#RRGGBB"}},
    {{"name": "Colour name", "hex": "#RRGGBB"}},
    {{"name": "Colour name", "hex": "#RRGGBB"}},
    {{"name": "Colour name", "hex": "#RRGGBB"}},
    {{"name": "Colour name", "hex": "#RRGGBB"}}
  ],
  "ideas": ["3 short suggestions to develop the sketch further"],
  "image_prompt": "A copy-ready image prompt, max 50 words, that follows the sketch's composition"
}}
Choose palette colours that suit the sketch. Do not name living artists or copyrighted characters.
Variation: {random.randint(1, 10**6)}
"""
            with st.spinner("Looking at your sketch..."):
                try:
                    raw = ask_gemini_image(prompt, _prepare(file), "image/jpeg").strip()
                    raw = raw[raw.find("{"): raw.rfind("}") + 1]
                    data = json.loads(raw)
                    if not data.get("what_i_see"):
                        raise ValueError("The answer was incomplete. Please try again.")
                    st.session_state.sk_data = data
                    st.session_state.sketch_prompt = str(data.get("image_prompt", ""))
                    st.session_state.sk_version = st.session_state.get("sk_version", 0) + 1
                except Exception as e:
                    st.warning("Gemini could not finish this one.")
                    st.code(f"{type(e).__name__}: {str(e)[:300]}")

    if "sk_data" in st.session_state:
        d = st.session_state.sk_data
        version = st.session_state.get("sk_version", 0)

        st.divider()
        label("sparkle", "What I see", "h3")
        st.markdown(html.escape(str(d.get("what_i_see", ""))))

        t_keep, t_pal, t_ideas, t_prompt = st.tabs(["Keep", "Palette", "Ideas", "Prompt"])
        with t_keep:
            for item in d.get("keep", []):
                st.markdown(f"- {html.escape(str(item))}")
        with t_pal:
            colours = [
                {
                    "name": str(c.get("name", "Colour"))[:40],
                    "hex": _hex(c.get("hex", "")),
                    "use": "",
                }
                for c in d.get("palette", [])[:5]
            ]
            components.html(_swatches(colours), height=230)
        with t_ideas:
            for item in d.get("ideas", []):
                st.markdown(f"- {html.escape(str(item))}")
        with t_prompt:
            st.text_area(
                "Image prompt (edit and copy)",
                value=str(d.get("image_prompt", "")),
                key=f"sk_prompt_{version}",
                height=130,
            )

        sheet = "PREVIS-IDEORA SKETCH GUIDE\n\n"
        sheet += f"What I see: {d.get('what_i_see', '')}\n\nKeep:\n"
        sheet += "".join(f"- {k}\n" for k in d.get("keep", []))
        sheet += "\nPalette:\n"
        sheet += "".join(f"- {c.get('name', '')} {c.get('hex', '')}\n" for c in d.get("palette", []))
        sheet += "\nIdeas:\n" + "".join(f"- {i}\n" for i in d.get("ideas", []))
        sheet += f"\nPrompt: {st.session_state.get(f'sk_prompt_{version}', d.get('image_prompt', ''))}\n"
        st.download_button("Download Sketch Notes", data=sheet, file_name="previs_ideora_sketch.txt", mime="text/plain")