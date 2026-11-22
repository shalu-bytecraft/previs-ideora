"""Feature 2: Palette Studio. Dynamic prompt-driven colour categories with tap-to-copy hex."""
import html
import json
import random
import re

import streamlit as st
import streamlit.components.v1 as components
import vault

from ai import ask_gemini

HARMONIES = ["Any", "Warm", "Earthy", "Pastel", "High contrast"]
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _swatches(colours):
    data = json.dumps(colours).replace("</", "<\\/")
    return """
<link href="https://fonts.googleapis.com/css2?family=Delicious+Handrawn&family=Gaegu&display=swap" rel="stylesheet">
<style>
body{margin:0;font-family:'Gaegu',cursive;color:#5C4A3F;background:transparent}
.sec{margin-bottom:22px}
.cat-title{font-family:'Delicious Handrawn',cursive;font-size:24px;color:#5C4A3F;margin:0 0 10px 4px;border-bottom:1.5px dashed rgba(92,74,63,.25);padding-bottom:4px}
.row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}
@media(max-width:640px){.row{grid-template-columns:repeat(2,minmax(0,1fr))}}
.card{min-width:0;cursor:pointer;text-align:center;transition:transform .2s;padding:6px;border-radius:14px}
.card:hover{transform:translateY(-4px) rotate(-1deg);background:rgba(92,74,63,.04)}
.sw{height:88px;border-radius:46% 54% 50% 50% / 55% 45% 55% 45%;box-shadow:2px 4px 0 rgba(92,74,63,.18);border:2px solid rgba(92,74,63,.12)}
.nm{font-family:'Delicious Handrawn',cursive;font-size:20px;margin-top:8px;line-height:1.1}
.hx{font-size:18px;font-weight:700}
.use{font-size:15px;opacity:.78;line-height:1.15;margin-top:2px}
.cp{font-size:14px;color:#B7766B;height:16px;margin-top:2px}
</style>
<div id="root"></div>
<script>
var C=""" + data + """;
var root=document.getElementById('root');

function fb(t,done){var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();try{document.execCommand('copy');}catch(e){}document.body.removeChild(a);done();}
function copy(t,el){
  var cp=el.querySelector('.cp');
  function done(){cp.textContent='copied!';setTimeout(function(){cp.textContent='tap to copy';},1300);}
  if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(done,function(){fb(t,done);});}else{fb(t,done);}
}

// Preserve the exact category order returned by Gemini
var seen=[];
C.forEach(function(c){
  var cat=c.category||'Palette';
  if(seen.indexOf(cat)===-1) seen.push(cat);
});

seen.forEach(function(cat){
  var items=C.filter(function(c){return (c.category||'Palette')===cat;});
  if(!items.length) return;
  var sec=document.createElement('div');sec.className='sec';
  var h=document.createElement('div');h.className='cat-title';h.textContent=cat;
  var row=document.createElement('div');row.className='row';
  items.forEach(function(c){
    var d=document.createElement('div');d.className='card';
    var s=document.createElement('div');s.className='sw';s.style.background=c.hex;
    var n=document.createElement('div');n.className='nm';n.textContent=c.name;
    var hx=document.createElement('div');hx.className='hx';hx.textContent=c.hex.toUpperCase();
    var u=document.createElement('div');u.className='use';u.textContent=c.use||'';
    var p=document.createElement('div');p.className='cp';p.textContent='tap to copy';
    d.append(s,n,hx,u,p);
    d.addEventListener('click',function(){copy(c.hex.toUpperCase(),d);});
    row.appendChild(d);
  });
  sec.append(h,row);
  root.appendChild(sec);
});
function resize(){
  if(window.frameElement){window.frameElement.style.height=(document.body.scrollHeight+24)+'px';}
}
resize();
setTimeout(resize,300);
</script>
"""


def palette_page(label, name, desc):
    st.markdown(f"<div class='panel'><h3>{name}</h3><p>{desc}</p></div>", unsafe_allow_html=True)

    idea = st.text_area(
        "Describe your idea or mood",
        value=st.session_state.get("concept_idea", ""),
        key="pal_idea",
        placeholder="Example: a forest spirit with glowing eyes under mossy trees",
        height=100,
    )
    harmony = st.radio("Colour harmony", HARMONIES, horizontal=True, key="pal_harmony")

    if st.button("Make Palette", key="pal_go"):
        if not idea.strip():
            st.warning("Please describe your idea or mood first.")
        else:
            style = "Choose whichever harmony suits the idea best." if harmony == "Any" else f"Harmony style: {harmony}."
            prompt = f"""
You are a colour designer helping a visual development artist. Support their taste, never replace it.
Idea or mood: {idea}
{style}

1. Analyze the subjects, materials, lighting, and elements inside the user's idea.
2. Invent 4 distinct, subject-specific categories tailored directly to what is in the prompt (for example, if the prompt is "forest spirit", use categories like "Moss & Foliage", "Spirit Glow", "Eyes", "Cloak"; if it is "cyberpunk street", use "Neon Signs", "Wet Asphalt", "Jacket & Gear", "Night Sky"). Do NOT use generic labels like "Primary" or "Secondary".
3. Under each of the 4 categories, generate 4 cohesive colours (16 colours total: base tone, shadow, midtone, and highlight/accent).
4. Give every colour an evocative, poetic artist colour name (like "Lichen Velvet", "Wisp Gold", "Midnight Pine") and a concise prompt-specific recommendation in "use".

Return ONLY valid JSON in this exact shape:
{{
  "palette": [
    {{"category": "Dynamic Category Name", "name": "Evocative Colour Name", "hex": "#RRGGBB", "use": "short prompt-based tip"}}
  ],
  "note": "One short sentence on why these colours work together"
}}
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
                            cat = html.unescape(str(c.get("category", "Palette"))).strip()[:35] or "Palette"
                            colours.append({
                                "category": cat,
                                "name": html.unescape(str(c.get("name", "Colour")))[:40],
                                "hex": hx,
                                "use": str(c.get("use", ""))[:65],
                            })
                    if not colours:
                        raise ValueError("No valid colours came back. Please try again.")
                    st.session_state.palette_data = {
                        "colours": colours[:20],
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

        # Group dynamically in the order categories appear
        ordered_cats = []
        for c in pd["colours"]:
            cat = c.get("category", "Palette")
            if cat not in ordered_cats:
                ordered_cats.append(cat)

        iframe_height = max(270, len(ordered_cats) * 265)
        components.html(_swatches(pd["colours"]), height=iframe_height)

        lines = [
            "PREVIS-IDEORA PALETTE",
            f"Idea: {pd['idea']}",
            f"Harmony: {pd['harmony']}",
            "",
        ]
        for cat in ordered_cats:
            lines.append(f"=== {cat.upper()} ===")
            for c in pd["colours"]:
                if c.get("category", "Palette") == cat:
                    lines.append(f"  {c['name']}: {c['hex'].upper()}  ({c['use']})")
            lines.append("")

        st.download_button(
            "Download Palette",
            data="\n".join(lines),
            file_name="previs_ideora_palette.txt",
            mime="text/plain",
        )
        if st.session_state.get("user"):
            p_col1, p_col2 = st.columns([3, 1])
            with p_col1:
                p_title = st.text_input(
                    "Palette title",
                    value=pd["idea"][:35] or "My Palette",
                    key="pal_save_title",
                    label_visibility="collapsed",
                )
            with p_col2:
                if st.button("💾 Save Palette", key="save_pal_btn", use_container_width=True):
                    vault.save_item(st.session_state.user, "Palette", p_title.strip() or "Untitled Palette", pd)
                    st.toast("Palette saved to your Studio Sketchbook!")