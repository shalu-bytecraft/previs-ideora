import random
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Previs Ideora", page_icon="🎨", layout="wide")


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