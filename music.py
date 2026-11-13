"""Soft background music + click sounds + a tiny paper-style on/off button.

Everything is generated in the browser with the Web Audio API,
so there are no audio files and no licence worries.

Use:  from music import add_sound   ...   add_sound()   (right after st.set_page_config)
"""
import json
import streamlit.components.v1 as components

_CODE = r"""
(function () {
  if (window.__previsSound) return;
  window.__previsSound = true;

  var AC = window.AudioContext || window.webkitAudioContext;
  var ctx, music, sfx, loop = null;
  var on = localStorage.getItem('previs_sound') !== 'off';

  var PENTA = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5];
  var CHORDS = [
    [130.81, 196.0, 261.63, 329.63],
    [110.0, 164.81, 220.0, 329.63],
    [87.31, 130.81, 174.61, 261.63],
    [98.0, 146.83, 196.0, 293.66]
  ];
  var bar = 0;

  function init() {
    if (ctx) return;
    ctx = new AC();
    music = ctx.createGain(); music.gain.value = 0;
    sfx = ctx.createGain(); sfx.gain.value = 1;
    var lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 1500;
    var echo = ctx.createDelay(); echo.delayTime.value = 0.5;
    var fb = ctx.createGain(); fb.gain.value = 0.35;
    music.connect(lp); lp.connect(ctx.destination);
    lp.connect(echo); echo.connect(fb); fb.connect(echo); echo.connect(ctx.destination);
    sfx.connect(ctx.destination);
  }

  function tone(dest, f, t, dur, vol, type, att) {
    var o = ctx.createOscillator(), g = ctx.createGain();
    o.type = type; o.frequency.value = f;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(vol, t + att);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(dest);
    o.start(t); o.stop(t + dur + 0.1);
  }

  function playBar() {
    var t = ctx.currentTime + 0.05;
    CHORDS[bar % CHORDS.length].forEach(function (f) { tone(music, f, t, 9, 0.05, 'sine', 3); });
    for (var i = 0; i < 3; i++) {
      var f = PENTA[Math.floor(Math.random() * PENTA.length)];
      tone(music, f, t + 1 + Math.random() * 6, 3.2, 0.035, 'triangle', 0.03);
    }
    bar++;
  }

  function startMusic() {
    init();
    ctx.resume();
    music.gain.cancelScheduledValues(ctx.currentTime);
    music.gain.linearRampToValueAtTime(1, ctx.currentTime + 3);
    if (!loop) { playBar(); loop = setInterval(playBar, 8000); }
  }

  function stopMusic() {
    if (!ctx) return;
    music.gain.cancelScheduledValues(ctx.currentTime);
    music.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.6);
    clearInterval(loop); loop = null;
  }

  function pop() {
    if (!ctx || ctx.state !== 'running') return;
    var f = PENTA[Math.floor(Math.random() * 4)] * 1.5;
    tone(sfx, f, ctx.currentTime, 0.35, 0.10, 'sine', 0.005);
    tone(sfx, f * 2, ctx.currentTime, 0.15, 0.03, 'triangle', 0.003);
  }

  /* ---------- the little paper button ---------- */
  var css = document.createElement('style');
  css.textContent = `
  [data-testid="stElementContainer"]:has(iframe[height="0"]){display:none;}
  #previs-sound{position:fixed;right:22px;bottom:22px;z-index:99999;width:50px;height:50px;
    border:2px dashed rgba(92,74,63,.45);border-radius:58% 42% 55% 45% / 48% 56% 44% 52%;
    background:#FBF3E4;box-shadow:2px 4px 0 rgba(92,74,63,.18);cursor:pointer;padding:0;
    display:flex;align-items:center;justify-content:center;transform:rotate(-4deg);
    transition:transform .25s,box-shadow .25s;}
  #previs-sound:hover{transform:rotate(3deg) translateY(-3px);box-shadow:3px 7px 0 rgba(92,74,63,.18);}
  #previs-sound svg{width:30px;height:30px;overflow:visible;}
  #previs-sound .note{animation:psBob 2.6s ease-in-out infinite alternate;transform-origin:50% 80%;}
  #previs-sound .wv{stroke:#C48B8B;opacity:0;animation:psWave 2.2s ease-in-out infinite;}
  #previs-sound .wv.b{animation-delay:-1.1s;}
  #previs-sound .slash{display:none;}
  #previs-sound.off .slash{display:block;}
  #previs-sound.off .note{animation:none;opacity:.5;}
  #previs-sound.off .wv{display:none;}
  @keyframes psBob{from{transform:rotate(-5deg);}to{transform:rotate(5deg) translateY(-1px);}}
  @keyframes psWave{0%{opacity:0;}50%{opacity:.9;}100%{opacity:0;}}
  @media (prefers-reduced-motion:reduce){#previs-sound .note,#previs-sound .wv{animation:none;}}
  `;
  document.head.appendChild(css);

  var btn = document.createElement('button');
  btn.id = 'previs-sound';
  btn.setAttribute('aria-label', 'Toggle soft music and sounds');
  btn.title = 'soft music';
  btn.innerHTML = `
  <svg viewBox="0 0 40 40" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <g class="note">
      <ellipse cx="15" cy="28" rx="5.2" ry="3.8" fill="#5C4A3F" stroke="#5C4A3F" stroke-width="1.6" transform="rotate(-18 15 28)"/>
      <path d="M19.6 26.5V9.5l9 3v5" stroke="#5C4A3F" stroke-width="2.4"/>
    </g>
    <path class="wv" d="M32 20q3 2.5 0 6" stroke-width="2"/>
    <path class="wv b" d="M35.5 18q5 4.5 0 10" stroke-width="2"/>
    <path class="slash" d="M7 7L33 34" stroke="#C48B8B" stroke-width="3"/>
  </svg>`;
  document.body.appendChild(btn);

  function paint() { btn.classList.toggle('off', !on); }
  paint();

  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    on = !on;
    localStorage.setItem('previs_sound', on ? 'on' : 'off');
    paint();
    if (on) { startMusic(); setTimeout(pop, 120); } else { stopMusic(); }
  });

  /* any other click: start music on the first one, then a soft pop on each */
  document.addEventListener('click', function (e) {
    if (!on || e.target.closest('#previs-sound')) return;
    if (!ctx || !loop) startMusic();
    pop();
  }, true);
})();
"""

_HTML = (
    "<script>(function(){var P=window.parent,D=P.document;"
    "var s=D.createElement('script');s.textContent="
    + json.dumps(_CODE)
    + ";D.head.appendChild(s);})();</script>"
)


def add_sound():
    """Call once, right after st.set_page_config()."""
    components.html(_HTML, height=0)