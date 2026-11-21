"""Feature 6: Character Keeper. Lock one character description and reuse it in every panel prompt."""
import json
import random
import re
from io import BytesIO

import streamlit as st
from PIL import Image, ImageOps

from ai import ask_gemini, ask_gemini_image

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _prepare(file):
    img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
    img.thumbnail((1024, 1024))
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def _chips(colours):
    out = ""
    for c in colours:
        hx = str(c.get("hex", "")).strip()
        if HEX.match(hx):
            out += (
                f'<span title="{c.get("name", "")} {hx.upper()}" style="display:inline-block;width:28px;'
                f'height:28px;border-radius:50%;background:{hx};margin:0 6px 6px 0;'
                f'border:1px solid rgba(92,74,63,.25)"></span>'
            )
    return out


def _lock(descriptor_key):
    st.session_state.character = {
        "name": st.session_state.ck_data["name"],
        "descriptor": st.session_state.get(descriptor_key, "").strip(),
    }
    st.session_state.ck_done = f"{st.session_state.character['name']} is locked in."


def _apply_to_storyboard():
    ch = st.session_state.character
    desc = ch["descriptor"]
    version = st.session_state.get("sb_version", 0)
    changed = 0
    for i, shot in enumerate(st.session_state.sb_data["shots"]):
        current = st.session_state.get(f"sb_prompt_{version}_{i}", shot.get("image_prompt", ""))
        if desc and desc in current:
            continue
        new = f"{desc} {current}".strip()
        shot["image_prompt"] = new
        st.session_state[f"sb_prompt_{version}_{i}"] = new
        changed += 1
    st.session_state.ck_done = (
        f"Added {ch['name']} to {changed} panel prompt(s). Open the Storyboard tab to see them."
    )


def character_keeper_page(label, name, desc):
    st.markdown(f"<div class='panel'><h3>{name}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    st.caption(
        "Describe or upload your character once. You get one locked description to paste at the start of every "
        "prompt, so the character keeps the same look in every panel."
    )

    msg = st.session_state.pop("ck_done", None)
    if msg:
        st.success(msg)

    cname = st.text_input("Character name", key="ck_name", placeholder="Example: Mira, the lantern fox")
    notes = st.text_area(
        "Describe your character (optional if you upload a drawing)",
        key="ck_notes",
        height=110,
        placeholder="Example: a small fox with a lantern, round glasses and a patched green scarf",
    )
    pic = st.file_uploader("Your character drawing (optional)", type=["png", "jpg", "jpeg", "webp"], key="ck_pic")
    if pic is not None:
        st.image(pic, width=220, caption="Your character")

    if st.button("Build Character Sheet", key="ck_go"):
        if not notes.strip() and pic is None:
            st.warning("Please describe your character or upload a drawing.")
        else:
            prompt = f"""
You are a character designer's assistant. Capture the artist's own character exactly. Never redesign it.
Character name: {cname.strip() or "Unnamed"}
Artist's notes: {notes.strip() or "(none, use the attached drawing)"}
If a drawing is attached, describe exactly what you see in it.

Return ONLY valid JSON in exactly this shape:
{{
  "name": "Character name",
  "summary": "One sentence about who the character is",
  "face": "Face shape and features",
  "hair": "Hair or fur: colour, length, style",
  "eyes": "Eye shape and colour",
  "build": "Body type, height, age impression",
  "outfit": "Clothing and accessories",
  "props": "Signature objects they carry",
  "expression": "Typical expression and body language",
  "colours": [{{"name": "Colour name", "hex": "#RRGGBB"}}, {{"name": "Colour name", "hex": "#RRGGBB"}}, {{"name": "Colour name", "hex": "#RRGGBB"}}, {{"name": "Colour name", "hex": "#RRGGBB"}}],
  "locked_descriptor": "One compact paragraph (40 to 70 words) that fully describes how this character always looks, written so it can be pasted at the start of any image prompt"
}}
Do not name living artists or copyrighted characters. Variation: {random.randint(1, 10**6)}
"""
            with st.spinner("Reading your character..."):
                try:
                    if pic is not None:
                        raw = ask_gemini_image(prompt, image_bytes=_prepare(pic), mime_type="image/jpeg")
                    else:
                        raw = ask_gemini(prompt)
                    raw = raw.strip()
                    data = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
                    if not data.get("locked_descriptor"):
                        raise ValueError("No description came back. Please try again.")
                    data["name"] = cname.strip() or str(data.get("name", "My Character"))
                    st.session_state.ck_data = data
                    st.session_state.ck_version = st.session_state.get("ck_version", 0) + 1
                except Exception as e:
                    st.warning("Gemini could not finish this one.")
                    st.code(f"{type(e).__name__}: {str(e)[:300]}")

    if "ck_data" in st.session_state:
        d = st.session_state.ck_data
        version = st.session_state.get("ck_version", 0)

        st.divider()
        label("person", "Character sheet", "h2")
        with st.container(border=True):
            st.markdown(f"**{d['name']}**. {d.get('summary', '')}")
            left, right = st.columns(2)
            with left:
                st.markdown(f"**Face:** {d.get('face', '')}")
                st.markdown(f"**Hair:** {d.get('hair', '')}")
                st.markdown(f"**Eyes:** {d.get('eyes', '')}")
                st.markdown(f"**Build:** {d.get('build', '')}")
            with right:
                st.markdown(f"**Outfit:** {d.get('outfit', '')}")
                st.markdown(f"**Props:** {d.get('props', '')}")
                st.markdown(f"**Expression:** {d.get('expression', '')}")
            st.markdown(_chips(d.get("colours", [])), unsafe_allow_html=True)

        with st.container(border=True):
            label("sparkle", "Locked description")
            st.caption("Edit it until it matches your character exactly. This text is what gets reused.")
            key = f"prompt_ck_locked_{version}"
            st.text_area("Locked description (edit and copy)", value=str(d["locked_descriptor"]), key=key, height=150)
            st.button("Lock this character", key="ck_lock", on_click=_lock, args=(key,))

        ch = st.session_state.get("character")
        if ch:
            st.divider()
            label("brush", f"Use {ch['name']}", "h3")
            if "sb_data" in st.session_state:
                st.button(
                    "Add to every Storyboard panel prompt",
                    key="ck_apply",
                    on_click=_apply_to_storyboard,
                )
            else:
                st.caption("Build a storyboard first, then come back to add this character to every panel prompt.")
