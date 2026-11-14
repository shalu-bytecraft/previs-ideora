"""Feature 5: Mood Board Maker. Palette, font pairings and keywords on one board."""
import json
import random
import re
import urllib.parse

import streamlit as st
import streamlit.components.v1 as components

from ai import ask_gemini

FONT_LIST = [
    "Playfair Display", "DM Serif Display", "Abril Fatface", "Cormorant Garamond", "Lora",
    "Merriweather", "Montserrat", "Poppins", "Raleway", "Quicksand", "Nunito", "Inter",
    "Space Grotesk", "Caveat", "Delicious Handrawn", "Gaegu", "Patrick Hand",
    "Special Elite", "Bebas Neue", "Josefin Sans",
]
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _board(data):
    fonts = sorted({f for p in data["fonts"] for f in (p["heading"], p["body"])})
    families = "&".join("family=" + urllib.parse.quote_plus(f) for f in fonts)
    payload = json.dumps(data).replace("</", "<\\/")
    return """
<link href="https://fonts.googleapis.com/css2?""" + families + """&display=swap" rel="stylesheet">
<style>
body{margin:0;color:#5C4A3F;font-family:'Gaegu',cursive;background:transparent}
.board{background:#FBF3E4;border-radius:10px;padding:20px;box-shadow:2px 4px 0 rgba(92,74,63,.18)}
.title{font-size:36px;line-height:1.1;margin:0 0 6px}
.stmt{font-size:18px;margin:0 0 16px}
.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.tile{padding:14px 16px;border-radius:8px 14px 10px 12px;box-shadow:2px 4px 0 rgba(92,74,63,.15);transform:rotate(var(--r))}
.full{grid-column:1/-1}
.tag{font-size:13px;letter-spacing:.04em;text-transform:uppercase;opacity:.6;margin-bottom:8px}
.sws{display:flex;gap:12px}
.sw{flex:1;text-align:center;font-size:14px}
.dot{height:70px;border-radius:46% 54% 50% 50% / 55% 45% 55% 45%;border:2px solid rgba(92,74,63,.12);margin-bottom:5px}
.hd{font-size:30px;line-height:1.1}
.bd{font-size:16px;margin-top:6px;line-height:1.35}
.nm{font-size:13px;opacity:.65;margin-top:8px}
.kw{display:inline-block;padding:4px 12px;margin:0 8px 8px 0;border-radius:6px 10px 7px 11px;font-size:17px;transform:rotate(var(--r))}
</style>
<div class="board" id="b"></div>
<script>
var D=""" + payload + """;
var T=['#F6EBDD','#F1D3C0','#E8D8C4','#EFE3D3','#F3DCD2'];
var R=['-1.2deg','.9deg','-.6deg','1.3deg','-1deg'];
var b=document.getElementById('b');
function el(t,c,x,p){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;(p||b).appendChild(e);return e;}
var h=D.fonts[0].heading,bo=D.fonts[0].body;
var ti=el('h1','title',D.title);ti.style.fontFamily="'"+h+"',serif";
var st=el('p','stmt',D.statement);st.style.fontFamily="'"+bo+"',sans-serif";
var g=el('div','grid');
var t1=el('div','tile full',null,g);t1.style.background=T[0];t1.style.setProperty('--r',R[0]);
el('div','tag','Palette',t1);var sw=el('div','sws',null,t1);
D.palette.forEach(function(c){var s=el('div','sw',null,sw);var d=el('div','dot',null,s);d.style.background=c.hex;el('div',null,c.name,s);el('div',null,c.hex.toUpperCase(),s);});
D.fonts.forEach(function(f,i){var t=el('div','tile',null,g);t.style.background=T[(i+1)%5];t.style.setProperty('--r',R[(i+1)%5]);
 el('div','tag','Font pairing '+(i+1),t);
 var a=el('div','hd','Aa '+f.heading,t);a.style.fontFamily="'"+f.heading+"',serif";
 var c=el('div','bd',f.why||'The quick brown fox jumps over the lazy dog.',t);c.style.fontFamily="'"+f.body+"',sans-serif";
 el('div','nm',f.heading+' + '+f.body,t);});
var t3=el('div','tile',null,g);t3.style.background=T[3];t3.style.setProperty('--r',R[3]);
el('div','tag','Keywords',t3);
D.keywords.forEach(function(k,i){var s=el('span','kw',k,t3);s.style.background=T[(i+2)%5];s.style.setProperty('--r',R[i%5]);});
var t4=el('div','tile',null,g);t4.style.background=T[4];t4.style.setProperty('--r',R[4]);
el('div','tag','Textures and materials',t4);
D.textures.forEach(function(k,i){var s=el('span','kw',k,t4);s.style.background=T[i%5];s.style.setProperty('--r',R[(i+2)%5]);});
</script>
"""


def mood_board_page(label, name, desc):
    st.markdown(f"<div class='panel'><h3>{name}</h3><p>{desc}</p></div>", unsafe_allow_html=True)

    idea = st.text_area(
        "Describe the project or mood",
        value=st.session_state.get("concept_idea", ""),
        key="mb_idea",
        placeholder="Example: a cosy autumn cafe brand for students",
        height=100,
    )
    own = st.session_state.get("palette_data")
    use_own = False
    if own:
        use_own = st.checkbox("Use my Palette Studio colours", value=True, key="mb_use_own")

    if st.button("Make Mood Board", key="mb_go"):
        if not idea.strip():
            st.warning("Please describe your project or mood first.")
        else:
            prompt = f"""
You are a creative director helping an artist build a mood board. Support their vision, never replace it.
Project or mood: {idea}

Return ONLY valid JSON in exactly this shape:
{{
  "title": "Short board title",
  "statement": "One or two sentences capturing the mood",
  "palette": [{{"name": "Colour name", "hex": "#RRGGBB"}}],
  "fonts": [
    {{"heading": "Font name", "body": "Font name", "why": "One short line on why this pairing fits"}},
    {{"heading": "Font name", "body": "Font name", "why": "One short line on why this pairing fits"}}
  ],
  "keywords": ["8 single words or short phrases"],
  "textures": ["4 textures or materials that suit the mood"]
}}
Give exactly 5 palette colours. Choose fonts ONLY from this list: {", ".join(FONT_LIST)}.
Variation: {random.randint(1, 10**6)}
"""
            with st.spinner("Pinning your board together..."):
                try:
                    raw = ask_gemini(prompt).strip()
                    raw = raw[raw.find("{"): raw.rfind("}") + 1]
                    d = json.loads(raw)

                    if use_own:
                        palette = [{"name": c["name"], "hex": c["hex"]} for c in own["colours"]]
                    else:
                        palette = [
                            {"name": str(c.get("name", "Colour"))[:40], "hex": str(c.get("hex", "")).strip()}
                            for c in d.get("palette", [])
                            if HEX.match(str(c.get("hex", "")).strip())
                        ][:5]
                    if not palette:
                        raise ValueError("No valid colours came back. Please try again.")

                    fonts = []
                    for p in d.get("fonts", []):
                        h, b = p.get("heading"), p.get("body")
                        if h in FONT_LIST and b in FONT_LIST:
                            fonts.append({"heading": h, "body": b, "why": str(p.get("why", ""))[:90]})
                    if not fonts:
                        fonts = [{"heading": "Playfair Display", "body": "Quicksand", "why": "A calm, classic pairing."}]

                    st.session_state.mb_data = {
                        "title": str(d.get("title", "Mood Board"))[:60],
                        "statement": str(d.get("statement", ""))[:220],
                        "palette": palette,
                        "fonts": fonts[:2],
                        "keywords": [str(k)[:30] for k in d.get("keywords", [])][:8],
                        "textures": [str(k)[:30] for k in d.get("textures", [])][:4],
                        "idea": idea,
                    }
                except Exception as e:
                    st.warning("Gemini could not finish this one.")
                    st.code(f"{type(e).__name__}: {str(e)[:300]}")

    if "mb_data" in st.session_state:
        d = st.session_state.mb_data
        st.divider()
        label("palette", "Your Mood Board", "h2")
        components.html(_board(d), height=820, scrolling=True)

        sheet = (
            f"PREVIS-IDEORA MOOD BOARD\n{d['title']}\nIdea: {d['idea']}\n\n{d['statement']}\n\nPALETTE\n"
            + "\n".join(f"{c['name']}: {c['hex'].upper()}" for c in d["palette"])
            + "\n\nFONT PAIRINGS\n"
            + "\n".join(f"{p['heading']} + {p['body']}: {p['why']}" for p in d["fonts"])
            + "\n\nKEYWORDS\n" + ", ".join(d["keywords"])
            + "\n\nTEXTURES\n" + ", ".join(d["textures"]) + "\n"
        )
        st.download_button("Download Mood Board Notes", data=sheet, file_name="previs_ideora_moodboard.txt", mime="text/plain")
