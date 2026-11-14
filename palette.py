"""Feature 2: Palette Studio. Five colours from an idea or mood, tap a swatch to copy its hex."""
import html
import json
import random
import re

import streamlit as st
import streamlit.components.v1 as components

from ai import ask_gemini

HARMONIES = ["Any", "Warm", "Earthy", "Pastel", "High contrast"]
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _swatches(colours):
    data = json.dumps(colours).replace("</", "<\\/")
    return """
<link href="https://fonts.googleapis.com/css2?family=Delicious+Handrawn&family=Gaegu&display=swap" rel="stylesheet">
<style>
body{margin:0;font-family:'Gaegu',cursive;color:#5C4A3F;background:transparent}
.row{display:flex;gap:14px}
.card{flex:1 1 0;min-width:0;cursor:pointer;text-align:center;transition:transform .2s}
.card:hover{transform:translateY(-4px) rotate(-1deg)}
.sw{height:96px;border-radius:46% 54% 50% 50% / 55% 45% 55% 45%;box-shadow:2px 4px 0 rgba(92,74,63,.18);border:2px solid rgba(92,74,63,.12)}
.nm{font-family:'Delicious Handrawn',cursive;font-size:20px;margin-top:8px;line-height:1.1}
.hx{font-size:18px}
.use{font-size:15px;opacity:.7}
.cp{font-size:14px;color:#B7766B;height:16px}
</style>
<div class="row" id="row"></div>
<script>
var C=""" + data + """;
var row=document.getElementById('row');
function fb(t,done){var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();try{document.execCommand('copy');}catch(e){}document.body.removeChild(a);done();}
function copy(t,el){
  var cp=el.querySelector('.cp');
  function done(){cp.textContent='copied!';setTimeout(function(){cp.textContent='tap to copy';},1300);}
  if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(done,function(){fb(t,done);});}else{fb(t,done);}
}
C.forEach(function(c){
  var d=document.createElement('div');d.className='card';
  var s=document.createElement('div');s.className='sw';s.style.background=c.hex;
  var n=document.createElement('div');n.className='nm';n.textContent=c.name;
  var h=document.createElement('div');h.className='hx';h.textContent=c.hex.toUpperCase();
  var u=document.createElement('div');u.className='use';u.textContent=c.use||'';
  var p=document.createElement('div');p.className='cp';p.textContent='tap to copy';
  d.append(s,n,h,u,p);
  d.addEventListener('click',function(){copy(c.hex.toUpperCase(),d);});
  row.appendChild(d);
});
</script>
"""


def palette_page(label, name, desc):
    st.markdown(f"<div class='panel'><h3>{name}</h3><p>{desc}</p></div>", unsafe_allow_html=True)

    idea = st.text_area(
        "Describe your idea or mood",
        value=st.session_state.get("concept_idea", ""),
        key="pal_idea",
        placeholder="Example: a quiet rainy evening in an old bookshop",
        height=100,
    )
    harmony = st.radio("Colour harmony", HARMONIES, horizontal=True, key="pal_harmony")

    if st.button("Make Palette", key="pal_go"):
        if not idea.strip():
            st.warning("Please describe your idea or mood first.")
        else:
            style = "Choose whichever harmony suits the idea best." if harmony == "Any" else f"Harmony style: {harmony}."
            prompt = f"""
You are a colour designer helping an artist. Support their taste, never replace it.
Idea or mood: {idea}
{style}

Return ONLY valid JSON in exactly this shape:
{{
  "palette": [
    {{"name": "Colour name", "hex": "#RRGGBB", "use": "short tip, e.g. background or accent"}}
  ],
  "note": "One short sentence on why these colours work together"
}}
Give exactly 5 colours that really fit the idea.
Variation: {random.randint(1, 10**6)}
"""
            with st.spinner("Mixing your colours..."):
                try:
                    raw = ask_gemini(prompt).strip()
                    raw = raw[raw.find("{"): raw.rfind("}") + 1]
                    data = json.loads(raw)
                    colours = []
                    for c in data.get("palette", []):
                        hx = str(c.get("hex", "")).strip()
                        if HEX.match(hx):
                            colours.append({
                                "name": html.unescape(str(c.get("name", "Colour")))[:40],
                                "hex": hx,
                                "use": str(c.get("use", ""))[:40],
                            })
                    if not colours:
                        raise ValueError("No valid colours came back. Please try again.")
                    st.session_state.palette_data = {
                        "colours": colours[:5],
                        "note": str(data.get("note", "")),
                        "idea": idea,
                        "harmony": harmony,
                    }
                except Exception as e:
                    st.warning("Gemini could not finish this one.")
                    st.code(f"{type(e).__name__}: {str(e)[:300]}")

    if "palette_data" in st.session_state:
        pd = st.session_state.palette_data
        st.divider()
        label("palette", "Your Palette", "h2")
        if pd["note"]:
            st.markdown(pd["note"])
        components.html(_swatches(pd["colours"]), height=270)
        sheet = "PREVIS-IDEORA PALETTE\n" + f"Idea: {pd['idea']}\nHarmony: {pd['harmony']}\n\n" + "\n".join(
            f"{c['name']}: {c['hex'].upper()}  ({c['use']})" for c in pd["colours"]
        )
        st.download_button("Download Palette", data=sheet, file_name="previs_ideora_palette.txt", mime="text/plain")
