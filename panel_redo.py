"""Feature 7: Panel Redo. Redo one storyboard shot or one style option without redoing the rest."""
import json
import random

import streamlit as st

from ai import ask_gemini


def _parse(raw):
    raw = raw.strip()
    return json.loads(raw[raw.find("{"): raw.rfind("}") + 1])


# ---------- storyboard shots ----------
def _apply_shot(i, new, version):
    st.session_state.sb_data["shots"][i] = new
    st.session_state[f"sb_prompt_{version}_{i}"] = new.get("image_prompt", "")
    st.session_state.pop("pr_new", None)
    st.session_state.pr_done = f"Shot {i + 1} updated. Open the Storyboard tab to see it."


def _redo_shot():
    sb = st.session_state.sb_data
    shots = sb["shots"]
    version = st.session_state.get("sb_version", 0)

    i = st.selectbox(
        "Which shot?",
        list(range(len(shots))),
        format_func=lambda n: f"Shot {n + 1}: {shots[n].get('shot_type', '')} - {str(shots[n].get('action', ''))[:50]}",
        key=f"pr_shot_{version}",
    )
    old = shots[i]
    with st.container(border=True):
        st.markdown(f"**Current:** {old.get('shot_type', '')} · {old.get('camera_angle', '')}")
        st.markdown(str(old.get("action", "")))
        st.caption(f"Mood: {old.get('mood', '')}")

    direction = st.text_input(
        "What should change?",
        key=f"pr_dir_{version}",
        placeholder="Example: make it night time, and get closer on the face",
    )

    if st.button("Redo This Shot", key="pr_go_shot"):
        if not direction.strip():
            st.warning("Please say what should change.")
            return
        others = "\n".join(
            f"Shot {n + 1}: {s.get('action', '')}" for n, s in enumerate(shots) if n != i
        )
        prompt = f"""
You are a storyboard artist's assistant. Redo ONE shot of an existing storyboard. Keep it consistent with the other shots.
Storyboard title: {sb.get('title', '')}
Story idea: {sb.get('idea', '')}
Other shots:
{others}

The shot to redo (Shot {i + 1}):
Type: {old.get('shot_type', '')}. Angle: {old.get('camera_angle', '')}.
Action: {old.get('action', '')}. Mood: {old.get('mood', '')}.

The artist wants this change: {direction}

Return ONLY valid JSON in exactly this shape:
{{
  "shot_type": "Wide, Medium, Close-up, Extreme close-up, Over-the-shoulder or Aerial",
  "camera_angle": "Eye level, Low angle, High angle, Bird's-eye or Dutch tilt",
  "action": "What happens in this shot, 1 or 2 sentences",
  "mood": "A few words on mood and lighting",
  "image_prompt": "A detailed, copy-ready image prompt for this panel"
}}
Do not name living artists or copyrighted characters. Variation: {random.randint(1, 10**6)}
"""
        with st.spinner("Redoing the shot..."):
            try:
                new = _parse(ask_gemini(prompt))
                if not new.get("action") or not new.get("image_prompt"):
                    raise ValueError("The new shot was incomplete. Please try again.")
                st.session_state.pr_new = {"kind": "shot", "i": i, "data": new, "version": version}
            except Exception as e:
                st.warning("Gemini could not finish this one.")
                st.code(f"{type(e).__name__}: {str(e)[:300]}")

    pending = st.session_state.get("pr_new")
    if pending and pending["kind"] == "shot" and pending["version"] == version and pending["i"] == i:
        new = pending["data"]
        st.divider()
        with st.container(border=True):
            st.markdown(f"**New version:** {new.get('shot_type', '')} · {new.get('camera_angle', '')}")
            st.markdown(str(new.get("action", "")))
            st.caption(f"Mood: {new.get('mood', '')}")
            st.text_area("New panel prompt", value=str(new.get("image_prompt", "")), key=f"pr_newprompt_{version}_{i}", height=120)
        st.button("Use this version", key="pr_use_shot", on_click=_apply_shot, args=(i, new, version))


# ---------- style options ----------
def _apply_style(i, new, version):
    st.session_state.lab_data["items"][i] = new
    st.session_state[f"lab_prompt_{version}_{i}"] = new.get("prompt", "")
    st.session_state.pop("pr_new", None)
    st.session_state.pr_done = f"{new.get('style', 'Style')} updated. Open the Style Lab tab to see it."


def _redo_style():
    lab = st.session_state.lab_data
    items = lab["items"]
    version = st.session_state.get("lab_version", 0)

    i = st.selectbox(
        "Which style?",
        list(range(len(items))),
        format_func=lambda n: str(items[n].get("style", f"Style {n + 1}")),
        key=f"pr_style_{version}",
    )
    old = items[i]
    with st.container(border=True):
        st.markdown(f"**Current:** {old.get('style', '')}")
        st.markdown(str(old.get("look", "")))

    direction = st.text_input(
        "What should change?",
        key=f"pr_sdir_{version}",
        placeholder="Example: softer colours, more rainy and moody",
    )

    if st.button("Redo This Style", key="pr_go_style"):
        if not direction.strip():
            st.warning("Please say what should change.")
            return
        prompt = f"""
You are an art mentor. Redo ONE style option for the artist's idea.
Idea: {lab.get('idea', '')}
Style: {old.get('style', '')}
The artist wants this change: {direction}

Return ONLY valid JSON in exactly this shape:
{{
  "style": "{old.get('style', '')}",
  "look": "1 or 2 sentences on how this idea would look in this style",
  "palette": [{{"hex": "#RRGGBB"}}, {{"hex": "#RRGGBB"}}, {{"hex": "#RRGGBB"}}, {{"hex": "#RRGGBB"}}],
  "technique": "1 or 2 sentences of practical tips: tools, brushes or methods",
  "best_for": "One short line on what this style suits",
  "prompt": "A detailed, copy-ready image generation prompt for this idea in this style"
}}
Do not name living artists or copyrighted characters. Variation: {random.randint(1, 10**6)}
"""
        with st.spinner("Redoing the style..."):
            try:
                new = _parse(ask_gemini(prompt))
                if not new.get("prompt"):
                    raise ValueError("The new style was incomplete. Please try again.")
                new["style"] = old.get("style", new.get("style", "Style"))
                new["palette"] = [
                    {"hex": str(c.get("hex", ""))} for c in new.get("palette", []) if isinstance(c, dict)
                ]
                st.session_state.pr_new = {"kind": "style", "i": i, "data": new, "version": version}
            except Exception as e:
                st.warning("Gemini could not finish this one.")
                st.code(f"{type(e).__name__}: {str(e)[:300]}")

    pending = st.session_state.get("pr_new")
    if pending and pending["kind"] == "style" and pending["version"] == version and pending["i"] == i:
        new = pending["data"]
        st.divider()
        with st.container(border=True):
            st.markdown(f"**New version:** {new.get('style', '')}")
            st.markdown(str(new.get("look", "")))
            st.markdown(f"**Technique:** {new.get('technique', '')}")
            st.text_area("New image prompt", value=str(new.get("prompt", "")), key=f"pr_newsprompt_{version}_{i}", height=120)
        st.button("Use this version", key="pr_use_style", on_click=_apply_style, args=(i, new, version))


# ---------- the page ----------
def panel_redo_page(label, name, desc):
    st.markdown(f"<div class='panel'><h3>{name}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    st.caption("Pick one part, say what to change, and only that part is rebuilt. You choose whether to keep the new version.")

    msg = st.session_state.pop("pr_done", None)
    if msg:
        st.success(msg)

    options = []
    if "sb_data" in st.session_state:
        options.append("Storyboard shot")
    if "lab_data" in st.session_state:
        options.append("Style option")
    if not options:
        st.info("Build a storyboard (Storyboard tab) or a style comparison (Style Lab tab) first, then come back to redo one part of it.")
        return

    what = st.radio("What would you like to redo?", options, horizontal=True, key="pr_what")
    label("brush", "Redo one part", "h2")
    if what == "Storyboard shot":
        _redo_shot()
    else:
        _redo_style()
