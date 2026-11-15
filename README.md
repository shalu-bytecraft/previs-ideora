# Previs Ideora — Studio Co-Pilot

**An AI idea-to-storyboard assistant that supports digital artists. The AI plans, the artist creates.**

Built by **Team Tetra Spectra** for **GeNarrative Clash 2026** , **[Domain:Digital Art & Visual Co-Pilots]**

- **Live demo:** `[add your Streamlit link here]`
- **Demo video:** `[add your video link here]`

---

## The problem

Artists lose hours before they draw a single line. They stare at a blank page, hesitate over colours, compare styles in their heads, and plan shots from scratch. Many AI tools try to replace the artist. Artists want the opposite: help with the planning, and full control over the result.

## Our solution

Previs Ideora turns **one line of idea** into a creative starting kit: a concept, a colour palette, a style comparison, a shot-by-shot storyboard and a mood board etc., Every result is **editable**, nothing is final, and the artist always owns the creative decisions. The AI only suggests.

---

## Features

| # | Feature | What it does | Status |
|---|---------|--------------|--------|
| 1 | **Idea to Concept** | One line becomes a character, scene, mood, story direction, five-colour palette and a copy-ready image prompt. Editable cards and a downloadable concept sheet. | Working |
| 2 | **Palette Studio** | Five colours from an idea or mood, with harmony options (Warm, Earthy, Pastel, High contrast). Tap a swatch to copy its hex code. | Working |
| 3 | **Style Lab** | The same idea explored in 2 or 3 painting styles: look, palette, technique tips and a prompt for each. | Working |
| 4 | **Storyboard** | A 3 to 8 shot list with shot type, camera angle, action, mood and a panel prompt, plus a framing sketch per shot. | Working |
| 5 | **Mood Board** | Palette, font pairings (real Google Fonts), keywords and textures on one pinned-paper board. Can reuse the Palette Studio colours. | Working |
| 8 | **Sketch Guide** | The artist uploads their own sketch. Gemini reads it and suggests what to keep, a palette, ideas and a prompt that follows the sketch. The sketch stays the master. | Working |
| — | **Studio Sketchbook** | Sign up or log in to save concepts, palettes and mood boards, then load or delete them later. | Working |
| 6 | Character Keeper | Reuse the first character so it stays consistent across panels. | Planned |
| 7 | Panel Redo | Redo one shot or style without redoing the whole project. | Planned |
| 9 | Prompt Coach | Improve prompts based on chosen style and mood. | Planned |
| 10 | Reference Library | Save characters, sketches and references for later projects. | Planned |
| 11 | Version History | Timeline of earlier versions that can be restored. | Planned |
| 12 | Export | PNG, JPG and a full PDF project brief. | Planned |

> **A note on images:** the tools produce **prompts, guides and framing sketches**, not generated pictures. Image generation needs a paid image quota on the Gemini API, which our free key does not have. The prompts can be pasted into any image tool the artist prefers.

---

## How it works

```
Artist's idea (or sketch)
        │
        ▼
 Streamlit page  ──►  prompt template  ──►  ai.py  ──►  Gemini API
        ▲                                     │
        │                                     ▼
 Editable cards  ◄──  JSON parsed  ◄──  structured JSON reply
        │
        ▼
 Download as text   or   Save to Studio Sketchbook (SQLite)
```

1. Each feature page builds a prompt that asks Gemini to **reply only in JSON** with a fixed set of keys.
2. `ai.py` sends the request, trying several models in order and **retrying** on temporary errors (429, 500, 503, 504). Replies are **cached for one hour**.
3. The JSON is cleaned and **validated** (for example, colours must be valid hex codes, fonts must come from an approved list) before being shown.
4. Results appear as editable fields. Ideas carry across tabs: an idea typed in Idea to Concept pre-fills Palette Studio, Style Lab and Storyboard, and a chosen style flows into Storyboard and Sketch Guide.

---

## The look

We wanted the tool to feel like an artist's desk, not a dashboard.

- Hand-drawn **crayon doodles** that gently wobble in the background
- A **paper-cut title**, with each letter on its own torn paper tile in a different typeface
- **Brush-stroke tabs** painted in warm nude colours
- Handwritten fonts and small hand-drawn icons
- Soft **background music and click sounds** generated in the browser with the Web Audio API (no audio files), with a minimal on/off button

---

## Tech stack

| Part | Technology |
|------|------------|
| App framework | Streamlit |
| AI | Google Gemini API via `google-genai` (`gemini-3.5-flash`, with `gemini-3.5-flash-lite` and `gemini-3.1-flash-lite` as fallbacks) |
| Image input | Pillow (sketch resizing for Gemini) |
| Storage | SQLite (`vault.py`) |
| Styling | Custom CSS, Google Fonts |
| Sound | Web Audio API (JavaScript, no files) |
| Hosting | Streamlit Community Cloud |

---

## Project structure

```
previs-ideora/
├── app.py            # Main app: layout, title, tabs, Idea to Concept, Sketchbook dialog
├── ai.py             # Gemini calls: text and image input, model fallback, retries, caching
├── palette.py        # Feature 2: Palette Studio
├── style_lab.py      # Feature 3: Style Lab
├── storyboard.py     # Feature 4: Storyboard
├── mood_board.py     # Feature 5: Mood Board
├── sketch.py         # Feature 8: Sketch Guide
├── vault.py          # Accounts and saved works (SQLite)
├── music.py          # Background music, click sounds, on/off button
├── style.css         # Theme, paper-cut title, brush-stroke tabs, boiling doodle background
├── check_models.py   # Helper: lists which Gemini models a key can use
├── requirements.txt
├── .streamlit/
│   └── config.toml   # Theme and static file serving
└── static/
    ├── strokes/      # Brush-stroke tab images
    ├── doodles/      # Crayon doodle drawings
    ├── icons/        # Hand-drawn heading icons
    └── frames/       # Storyboard framing sketches
```

---

## Run it on your own computer

**You need:** Python 3.10 or newer, and a free Gemini API key from [Google AI Studio](https://aistudio.google.com).

```bash
# 1. Get the code
git clone https://github.com/shalu-bytecraft/previs-ideora.git
cd previs-ideora

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac or Linux

# 3. Install the libraries
pip install -r requirements.txt

# 4. Add your API key
#    Create the file .streamlit/secrets.toml and put this in it:
#    GEMINI_API_KEY = "your-key-here"

# 5. Run
streamlit run app.py
```

Then open **http://localhost:8501**.

## Deploy on Streamlit Community Cloud

1. Push the project to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), click **Create app**, and pick this repo, the `main` branch and `app.py`.
3. Open **Advanced settings** and paste `GEMINI_API_KEY = "your-key-here"` into **Secrets**.
4. Click **Deploy**.

---

## Design principles

- **The artist stays in charge.** Every output is editable. The AI suggests, the artist decides.
- **Support, not replace.** Sketch Guide treats the artist's drawing as the master and never redraws over it.
- **No names of living artists or copyrighted characters** in generated prompts.
- **Free to run.** Everything works on a free Gemini key.

## Known limitations

- No picture generation yet (needs a paid image quota). Prompts are provided instead.
- Gemini replies are not always identical. Re-running a feature gives a fresh variation.
- On the free hosting tier, the saved-works database can reset when the app restarts.
- Six of the twelve planned features are still to come (see the Features table).

## Roadmap

## *Features yet to be functional*

• Character Keeper
• Panel Redo
• Prompt Coach
• Reference Library
• Version History 
• One-click Export (PNG, JPG, PDF) & real image generation once an image quota is available.

---

## Team Tetra Spectra 

| Member | Contribution |
|--------|--------------|
| **Sameehita Ghosh (Team Lead)** | Team host. Handled registration, built the UI, assisted with coding and suggested features, project idea. |
| **Shalu Kumari** | Wrote the code, structured the project and built the Streamlit app. |
| **Tiyasha Bhattacharya** | Added special features and tools to the UI, added features and built the MVP, Project idea. |
| **Mohip Ghosh** | Suggested features to add and built the MVP. |

---

*Made with care for artists, at GeNarrative Clash 2026.*
