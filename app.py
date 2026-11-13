from music import add_sound

import random
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Previs Ideora", page_icon="🎨", layout="wide")
add_sound()


def load_css(path):
    css = Path(path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


FONTS = ["Abril Fatface", "Playfair Display", "Special Elite", "DM Serif Display",
         "Rye", "Shadows Into Light", "Caveat Brush"]
PAPER = ["#FBF6EE", "#EAD9C6", "#DCC3A5", "#E3B9A8", "#F1D3C0", "#E8C4CB"]
INK = ["#5C4A3F", "#B7766B", "#8A5A4D", "#A68A78"]


def torn_polygon(rnd):
    r = rnd.uniform
    pts = [
        (r(0, 5), r(0, 7)), (r(30, 45), r(0, 4)), (r(60, 75), r(0, 5)), (r(94, 100), r(0, 7)),
        (r(95, 100), r(40, 55)), (r(93, 100), r(93, 100)),
        (r(60, 75), r(95, 100)), (r(30, 45), r(94, 100)), (r(0, 6), r(93, 100)),
        (r(0, 5), r(60, 72)), (r(0, 4), r(25, 40)),
    ]
    return ",".join(f"{x:.1f}% {y:.1f}%" for x, y in pts)


def paper_title(words):
    rnd = random.Random(11)
    n = 0
    rows = []
    for word in words:
        tiles = []
        for ch in word:
            family = f"'{FONTS[n % len(FONTS)]}', serif"
            bg = PAPER[rnd.randrange(len(PAPER))]
            ink = INK[rnd.randrange(len(INK))]
            tilt = rnd.uniform(-7, 7)
            w, h = rnd.randint(52, 70), rnd.randint(64, 84)
            poly = torn_polygon(rnd)
            tiles.append(
                f'<span class="tile-wrap" style="--t:{tilt:.1f}deg;animation-delay:{n * 0.3:.1f}s">'
                f'<span class="tile" style="width:{w}px;height:{h}px;background-color:{bg};'
                f'color:{ink};font-family:{family};clip-path:polygon({poly})">{ch}</span></span>'
            )
            n += 1
        rows.append('<div class="title-row">' + "".join(tiles) + "</div>")
    return '<div class="title-block">' + "".join(rows) + "</div>"


load_css("style.css")

st.markdown(paper_title(["PREVIS", "IDEORA"]), unsafe_allow_html=True)
st.markdown('<p class="tagline">Studio Co-Pilot</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtext">One idea in. A concept, a palette, a storyboard and a mood board out. '
    "The AI plans, the artist creates.</p>",
    unsafe_allow_html=True,
)
FEATURES = [
    ("Idea to Concept", "One line becomes a character, a scene and a copy-ready image prompt. No more blank page."),
    ("Palette Studio", "Five harmonious colours from your idea or mood. Tap a swatch to copy its code."),
    ("Style Lab", "See the same idea in three painting styles side by side before you commit."),
    ("Storyboard", "A shot list with shot type, camera angle, action and mood, plus an image per shot."),
    ("Mood Board", "Palette, font pairings and keywords on one board, ready for a client pitch."),
    ("Character Keeper", "Reuses your first character image so it looks the same in every panel."),
    ("Panel Redo", "Redo a single shot or style without redoing the whole project."),
    ("Sketch Guide", "Upload your own sketch and the AI follows your work, not the other way round."),
    ("Prompt Coach", "Suggests better prompts based on your chosen art style and mood."),
    ("Reference Library", "Save characters, sketches and references to reuse in future projects."),
    ("Version History", "A timeline of earlier versions so you can restore an older design."),
    ("Export", "Download PNG, JPG or a full PDF project brief for a client or team."),
]
TEXT_COLOURS = ["#5C4A3F", "#FBF6EE", "#5C4A3F", "#FBF6EE", "#5C4A3F", "#FBF6EE",
                "#FBF6EE", "#FBF6EE", "#5C4A3F", "#5C4A3F", "#5C4A3F", "#5C4A3F"]

if "tab" not in st.session_state:
    st.session_state.tab = 0


def pick(i):
    st.session_state.tab = i


def tab_css():
    rules = []
    for i in range(12):
        n = f"{i + 1:02d}"
        rules.append(
            f'.st-key-tab_{n} button, .st-key-tabon_{n} button {{'
            f'background-image: url("app/static/strokes/stroke-{n}.png");'
            f'--d: {5 + (i % 5) * 0.9:.1f}s; --dl: {i * 0.4:.1f}s;'
            f'}}'
            f'.st-key-tab_{n} button p, .st-key-tabon_{n} button p {{'
            f'color: {TEXT_COLOURS[i]} !important;'
            f'}}'
        )
    return "".join(rules)


st.markdown(f"<style>{tab_css()}</style>", unsafe_allow_html=True)

for row in range(3):
    cols = st.columns(4)
    for c in range(4):
        i = row * 4 + c
        key = ("tabon_" if i == st.session_state.tab else "tab_") + f"{i + 1:02d}"
        with cols[c]:
            st.button(FEATURES[i][0], key=key, on_click=pick, args=(i,))

name, desc = FEATURES[st.session_state.tab]
st.markdown(
    f'<div class="panel"><h3>{name}</h3><p>{desc}</p>'
    f'<p class="soon">This feature is coming soon.</p></div>',
    unsafe_allow_html=True,
)