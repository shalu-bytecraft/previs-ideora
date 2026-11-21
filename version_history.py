"""Feature 11: Version History. Save snapshots of your work and restore an older design."""
import copy
import html
import json
import re
import uuid
from datetime import datetime

import streamlit as st

import vault

CATEGORY = "Version"
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")

# part name -> session keys that hold it (the first key must exist for the part to count)
PARTS = {
    "Concept": ["concept_data", "concept_idea"],
    "Palette": ["palette_data"],
    "Style Lab": ["lab_data"],
    "Storyboard": ["sb_data"],
    "Mood Board": ["mb_data"],
    "Character": ["ck_data", "character"],
}
# parts whose text boxes are keyed by a version number, so they need a bump after a restore
VERSION_KEYS = {
    "Concept": "concept_version",
    "Style Lab": "lab_version",
    "Storyboard": "sb_version",
    "Character": "ck_version",
}


def _plain(value):
    return json.loads(json.dumps(value, default=str))


def _now():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")


def _load():
    user = st.session_state.get("user")
    out = []
    if user:
        for item_id, _cat, title, content, created in vault.get_items(user, CATEGORY):
            try:
                parts = json.loads(content).get("parts", {})
            except Exception:
                continue
            out.append({"id": item_id, "name": title, "time": created, "parts": parts})
        out.sort(key=lambda v: v["id"], reverse=True)
    else:
        out = list(reversed(st.session_state.get("vh_list", [])))
    return out


def _save(name, chosen):
    parts = {}
    for part in chosen:
        parts[part] = {k: _plain(st.session_state[k]) for k in PARTS[part] if k in st.session_state}
    user = st.session_state.get("user")
    if user:
        vault.save_item(user, CATEGORY, name, {"parts": parts})
    else:
        st.session_state.setdefault("vh_list", []).append(
            {"id": uuid.uuid4().hex, "name": name, "time": _now(), "parts": parts}
        )


def _delete(version_id):
    if st.session_state.get("user"):
        vault.delete_item(version_id)
    else:
        st.session_state.vh_list = [v for v in st.session_state.get("vh_list", []) if v["id"] != version_id]


def _restore(name, parts):
    for part, values in parts.items():
        for key, value in values.items():
            st.session_state[key] = copy.deepcopy(value)
        vkey = VERSION_KEYS.get(part)
        if vkey:
            st.session_state[vkey] = st.session_state.get(vkey, 0) + 1
    st.session_state.vh_done = f"Restored “{name}”. Open the tabs to see it."


def _summary(part, values):
    if part == "Concept":
        return f"**Concept:** {str(values.get('concept_idea', ''))[:90]}"
    if part == "Palette":
        cols = (values.get("palette_data") or {}).get("colours", [])
        dots = "".join(
            f'<span style="display:inline-block;width:18px;height:18px;border-radius:50%;'
            f'background:{c["hex"]};margin-right:4px;border:1px solid rgba(92,74,63,.3)"></span>'
            for c in cols if isinstance(c, dict) and HEX.match(str(c.get("hex", "")))
        )
        return f"**Palette:** {dots}"
    if part == "Style Lab":
        names = [str(i.get("style", "")) for i in (values.get("lab_data") or {}).get("items", [])]
        return f"**Style Lab:** {', '.join(names)}"
    if part == "Storyboard":
        sb = values.get("sb_data") or {}
        return f"**Storyboard:** {sb.get('title', '')} ({len(sb.get('shots', []))} shots)"
    if part == "Mood Board":
        return f"**Mood Board:** {(values.get('mb_data') or {}).get('title', '')}"
    if part == "Character":
        return f"**Character:** {(values.get('ck_data') or {}).get('name', '')}"
    return f"**{part}**"


def version_history_page(label, name, desc):
    st.markdown(f"<div class='panel'><h3>{name}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    if st.session_state.get("user"):
        st.caption("Your versions are saved to your Studio Sketchbook account.")
    else:
        st.caption("Log in (the ☰ button, top left) to keep versions between visits. Without an account they last until you refresh the page.")

    msg = st.session_state.pop("vh_done", None)
    if msg:
        st.success(msg)

    available = [p for p, keys in PARTS.items() if keys[0] in st.session_state]

    label("paper", "Save a version", "h2")
    if not available:
        st.info("Make something first (a concept, palette, style comparison, storyboard, mood board or character), then come back to save a version of it.")
    else:
        with st.form("vh_form", clear_on_submit=True):
            vname = st.text_input("Version name", placeholder="Example: First idea, before the colour change")
            chosen = st.multiselect("What to include", available, default=available)
            go = st.form_submit_button("Save Version")
        if go:
            if not chosen:
                st.warning("Please include at least one part.")
            else:
                _save(vname.strip()[:60] or f"Version {_now()}", chosen)
                st.success("Version saved.")
        st.caption("A version keeps what each tab last built. Text you typed but did not regenerate is not included.")

    st.divider()
    label("book", "Timeline", "h2")
    versions = _load()
    if not versions:
        st.caption("No versions yet. Save one above and it will appear here.")
        return

    for v in versions:
        with st.container(border=True):
            label("sparkle", html.escape(str(v["name"])))
            st.caption(str(v["time"]))
            for part, values in v["parts"].items():
                st.markdown(_summary(part, values), unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                st.button(
                    "Restore this version",
                    key=f"vh_restore_{v['id']}",
                    on_click=_restore,
                    args=(v["name"], v["parts"]),
                )
            with b2:
                if st.button("Delete", key=f"vh_del_{v['id']}"):
                    _delete(v["id"])
                    st.rerun()
