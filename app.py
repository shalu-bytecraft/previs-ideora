from music import add_sound
import random
import json

from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Previs Ideora", page_icon="🎨", layout="wide")
add_sound()
from ai import ask_gemini
from palette import palette_page
from style_lab import style_lab_page

def load_css(path):
    css = Path(path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# Extra look-and-feel: thinner handwritten labels + little crayon icons beside headings
EXTRA_CSS = (
    'h1,h2,h3,h4,[data-testid="stHeading"] *{font-weight:400 !important;}'
    '[class*="st-key-tab"] button p{font-weight:400 !important;}'
    '.lbl{display:flex;align-items:center;gap:.55rem;margin:.2rem 0 .6rem;padding:0;'
    "font-family:'Delicious Handrawn','Gaegu',cursive;font-weight:400;color:#5C4A3F;line-height:1.1;}"
    'h2.lbl{font-size:2.1rem;}h3.lbl{font-size:1.6rem;}'
    '.lbl img{width:34px;height:34px;flex:none;}'
)


def label(icon, text, size="h3"):
    """A heading with a hand-drawn crayon icon instead of an emoji."""
    st.markdown(
        f'<{size} class="lbl"><img src="/app/static/icons/{icon}.svg" alt="">{text}</{size}>',
        unsafe_allow_html=True,
    )


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
st.markdown(f"<style>{EXTRA_CSS}</style>", unsafe_allow_html=True)

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




if st.session_state.tab == 0:

    st.markdown(
        f"<div class='panel'><h3>{name}</h3><p>{desc}</p></div>",
        unsafe_allow_html=True
    )

    idea = st.text_area(
        "Describe your creative idea",
        placeholder="Example: A magical forest with glowing butterflies...",
        height=120
    )
    if st.button("Generate Concept"):

        if not idea.strip():
            st.warning("Please enter your idea first.")

        else:
            with st.spinner("Developing your creative concept..."):
                try:
                    prompt = f"""
                    You are a creative assistant for artists.
                    Your job is to SUPPORT artists, never replace their creativity.

Develop this idea:
{idea}

Return ONLY valid JSON with these exact keys:

{{
  "character": "Character description",
  "scene": "Scene and environment description",
  "mood": "Mood, atmosphere and lighting",
  "palette": [
    {{"name": "Colour name", "hex": "#RRGGBB"}},
    {{"name": "Colour name", "hex": "#RRGGBB"}},
    {{"name": "Colour name", "hex": "#RRGGBB"}},
    {{"name": "Colour name", "hex": "#RRGGBB"}},
    {{"name": "Colour name", "hex": "#RRGGBB"}}
  ],
  "story": "Short story direction",
  "image_prompt": "Detailed image generation prompt"
}}

Choose five palette colours that really suit the idea.
Keep the suggestions original, useful and editable.
Do not make creative decisions final for the artist.
"""
                    raw_text = ask_gemini(prompt).strip()
                    # keep only the JSON object, whatever wrapping Gemini adds around it
                    raw_text = raw_text[raw_text.find("{"): raw_text.rfind("}") + 1]
                    concept = json.loads(raw_text)

                    st.session_state.concept_data = concept
                    st.session_state.concept_idea = idea
                    st.session_state.concept_version = (
                        st.session_state.get("concept_version", 0) + 1
                    )
                except Exception as e:
                    st.warning("Gemini could not finish this one.")
                    st.code(f"{type(e).__name__}: {str(e)[:300]}")

    # Display generated concept
    if "concept_data" in st.session_state:

        concept = st.session_state.concept_data
        version = st.session_state.concept_version

        st.divider()
        label("brush", "Your Creative Concept", "h2")

        # Separate editable cards
        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                label("person", "Character")
                character = st.text_area(
                    "Edit character",
                    value=concept.get("character", ""),
                    key=f"character_{version}"
                )

            with st.container(border=True):
                label("moon", "Mood &amp; Atmosphere")
                mood = st.text_area(
                    "Edit mood",
                    value=concept.get("mood", ""),
                    key=f"mood_{version}"
                )

            with st.container(border=True):
                label("book", "Story Direction")
                story = st.text_area(
                    "Edit story",
                    value=concept.get("story", ""),
                    key=f"story_{version}"
                )

        with col2:
            with st.container(border=True):
                label("tree", "Scene")
                scene = st.text_area(
                    "Edit scene",
                    value=concept.get("scene", ""),
                    key=f"scene_{version}"
                )

            with st.container(border=True):
                label("palette", "Color Palette")

                palette = concept.get("palette", [])

                for colour in palette:
                    st.markdown(
                        f"**{colour.get('name', 'Colour')}** — "
                        f"`{colour.get('hex', '')}`"
                    )

            with st.container(border=True):
                label("sparkle", "Image Generation Prompt")
                image_prompt = st.text_area(
                    "Edit image prompt",
                    value=concept.get("image_prompt", ""),
                    key=f"prompt_{version}"
                )

        # Complete concept sheet
        st.divider()
        label("paper", "Creative Concept Sheet", "h2")

        concept_sheet = f"""
PREVIS-IDEORA
CREATIVE CONCEPT SHEET

ORIGINAL IDEA:
{st.session_state.concept_idea}

CHARACTER:
{character}

SCENE:
{scene}

MOOD & ATMOSPHERE:
{mood}

COLOR PALETTE:
{chr(10).join(str(c.get('name', 'Colour')) + ': ' + str(c.get('hex', '')) for c in palette)}

STORY DIRECTION:
{story}

IMAGE GENERATION PROMPT:
{image_prompt}

Created with Previs-Ideora.
The artist owns the final creative decisions.
"""

        st.text_area(
            "Your complete concept sheet",
            value=concept_sheet,
            height=350,
            key=f"sheet_{version}"
        )

        st.download_button(
            "Download Concept Sheet",
            data=concept_sheet,
            file_name="previs_ideora_concept.txt",
            mime="text/plain"
        )
elif st.session_state.tab == 1:
     palette_page(label, name, desc)
    
elif st.session_state.tab == 2:
    style_lab_page(label, name, desc)
else:
    st.markdown(
        f'<div class="panel"><h3>{name}</h3><p>{desc}</p>'
        f'<p class="soon">This feature is coming soon.</p></div>',
        unsafe_allow_html=True,
    )

