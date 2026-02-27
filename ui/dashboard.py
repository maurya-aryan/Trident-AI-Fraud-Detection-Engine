"""
TRIDENT — AI Fraud Detection Dashboard
Clean, attractive dark UI with mouse-parallax particle background.
Run: streamlit run ui/dashboard.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import requests

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TRIDENT · AI Fraud Detection",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #060b18 !important;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none; }
.block-container { padding-top: 0 !important; max-width: 1200px; }

[data-testid="stTabs"] [role="tablist"] {
    gap: 4px; background: rgba(255,255,255,0.04);
    border-radius: 12px; padding: 4px;
}
[data-testid="stTabs"] button[role="tab"] {
    border-radius: 8px !important; color: #94a3b8 !important;
    font-weight: 600; font-size: 0.85rem; padding: 8px 20px !important; transition: all 0.2s;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg,#0080ff22,#00d4ff22) !important;
    color: #00d4ff !important; box-shadow: 0 0 16px #00d4ff33;
}

[data-testid="stButton"] > button {
    background: linear-gradient(135deg,#0080ff,#00d4ff) !important;
    color: #000 !important; font-weight: 700 !important;
    border: none !important; border-radius: 10px !important;
    padding: 10px 28px !important; letter-spacing: 0.5px; transition: all 0.2s;
    box-shadow: 0 4px 24px #00d4ff44;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-2px); box-shadow: 0 8px 32px #00d4ff66 !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
    color: #e2e8f0 !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #00d4ff !important; box-shadow: 0 0 0 2px #00d4ff22 !important;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 16px !important;
}

.trident-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(0,212,255,0.12);
    border-radius: 14px; padding: 20px 24px; margin-bottom: 16px;
}

.risk-banner {
    border-radius: 14px; padding: 20px 28px;
    margin-bottom: 20px; border-left: 5px solid;
}

.score-row { margin-bottom: 10px; }
.score-label { font-size: 0.82rem; color: #94a3b8; margin-bottom: 3px; }
.score-track {
    height: 8px; background: rgba(255,255,255,0.07);
    border-radius: 99px; overflow: hidden;
}
.score-fill { height: 100%; border-radius: 99px; }

[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Mouse-parallax particle background ───────────────────────────────────────
components.html("""
<style>
  #pcanvas { position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:0; }
</style>
<canvas id="pcanvas"></canvas>
<script>
(function(){
  const c = document.getElementById('pcanvas');
  const ctx = c.getContext('2d');
  let W = window.innerWidth, H = window.innerHeight;
  let mx = W/2, my = H/2;
  c.width = W; c.height = H;
  window.addEventListener('resize', () => { W=window.innerWidth; H=window.innerHeight; c.width=W; c.height=H; });
  try { window.parent.document.addEventListener('mousemove', e => { mx=e.clientX; my=e.clientY; }); } catch(e){}
  const pts = Array.from({length:85}, () => ({
    x: Math.random()*W, y: Math.random()*H,
    vx: (Math.random()-.5)*.4, vy: (Math.random()-.5)*.4,
    r: Math.random()*1.6+.5, a: Math.random()*.45+.12
  }));
  function frame(){
    ctx.clearRect(0,0,W,H);
    // glow under cursor
    const g = ctx.createRadialGradient(mx,my,0,mx,my,320);
    g.addColorStop(0,'rgba(0,128,255,0.07)'); g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
    // grid
    ctx.strokeStyle='rgba(0,212,255,0.025)'; ctx.lineWidth=1;
    for(let x=0;x<W;x+=60){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
    for(let y=0;y<H;y+=60){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
    // particles
    for(const p of pts){
      const dx=mx-p.x, dy=my-p.y, d=Math.hypot(dx,dy);
      if(d<200){ p.vx+=dx/d*.011; p.vy+=dy/d*.011; }
      p.vx*=.985; p.vy*=.985; p.x+=p.vx; p.y+=p.vy;
      if(p.x<0)p.x=W; if(p.x>W)p.x=0; if(p.y<0)p.y=H; if(p.y>H)p.y=0;
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle=`rgba(0,212,255,${p.a})`; ctx.fill();
    }
    // connections
    for(let i=0;i<pts.length;i++) for(let j=i+1;j<pts.length;j++){
      const dx=pts[i].x-pts[j].x, dy=pts[i].y-pts[j].y, d=Math.hypot(dx,dy);
      if(d<115){ ctx.beginPath(); ctx.strokeStyle=`rgba(0,212,255,${.13*(1-d/115)})`; ctx.lineWidth=.6;
        ctx.moveTo(pts[i].x,pts[i].y); ctx.lineTo(pts[j].x,pts[j].y); ctx.stroke(); }
    }
    requestAnimationFrame(frame);
  }
  frame();
})();
</script>
""", height=0, scrolling=False)

# ── Cached TRIDENT ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Initialising TRIDENT engine…")
def load_trident():
    from core.trident import TRIDENT
    return TRIDENT()

# ── Constants & helpers ───────────────────────────────────────────────────────
RISK_COLORS  = {"CRITICAL":"#ff0040","HIGH":"#ff6b00","MEDIUM":"#ffbf00","LOW":"#00e676"}
ACTION_ICONS = {"BLOCK":"🚫","ESCALATE":"⚠️","WARN":"⚡","VERIFY":"✅"}
MODULE_LABELS = {
    "ai_text_score":        "AI-Generated Text",
    "credential_score":     "Credential Exposure",
    "malware_score":        "Malware / Attachment",
    "email_phishing_score": "Email Phishing",
    "url_score":            "Malicious URL",
    "injection_score":      "Prompt Injection",
}

def bar_color(v):
    return "#ff0040" if v>=75 else "#ff6b00" if v>=50 else "#ffbf00" if v>=25 else "#00e676"

def render_module_bars(scores: dict):
    html = ""
    for key, label in MODULE_LABELS.items():
        v = scores.get(key, 0)
        c = bar_color(v)
        html += f"""
        <div class="score-row">
          <div class="score-label">{label}<b style="color:{c};float:right">{v:.0f}</b></div>
          <div class="score-track"><div class="score-fill" style="width:{v}%;background:{c}"></div></div>
        </div>"""
    st.markdown(f'<div class="trident-card">{html}</div>', unsafe_allow_html=True)

def gauge_fig(score, band, height=220):
    color = RISK_COLORS.get(band, "#888")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"font":{"size":42,"color":color},"suffix":"/100"},
        gauge={
            "axis":{"range":[0,100],"tickfont":{"color":"#64748b","size":9},"tickwidth":1,"tickcolor":"#334155"},
            "bar":{"color":color,"thickness":0.28},
            "bgcolor":"rgba(0,0,0,0)","borderwidth":0,
            "steps":[
                {"range":[0,25],"color":"rgba(0,230,118,0.07)"},
                {"range":[25,50],"color":"rgba(255,191,0,0.07)"},
                {"range":[50,75],"color":"rgba(255,107,0,0.07)"},
                {"range":[75,100],"color":"rgba(255,0,64,0.07)"},
            ],
            "threshold":{"line":{"color":color,"width":3},"thickness":0.9,"value":score},
        },
    ))
    fig.update_layout(height=height, margin=dict(l=20,r=20,t=20,b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
    return fig

def radar_fig(scores: dict):
    labels = [MODULE_LABELS.get(k,k) for k in scores]
    values = list(scores.values())
    labels.append(labels[0]); values.append(values[0])
    fig = go.Figure(go.Scatterpolar(
        r=values, theta=labels, fill='toself',
        fillcolor='rgba(0,128,255,0.10)',
        line=dict(color='#00d4ff', width=1.5),
        marker=dict(size=5, color='#00d4ff'),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,100], tickfont=dict(color="#64748b",size=9),
                            gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.05)"),
            angularaxis=dict(tickfont=dict(color="#94a3b8",size=10),
                             gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.05)"),
        ),
        height=260, margin=dict(l=44,r=44,t=20,b=20),
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
    )
    return fig

# ── Result renderer ───────────────────────────────────────────────────────────
def display_result(result):
    band   = result.risk_band
    action = result.recommended_action
    color  = RISK_COLORS.get(band, "#888")
    icon   = ACTION_ICONS.get(action, "❓")

    # Banner
    st.markdown(f"""
    <div class="risk-banner" style="background:{color}12;border-color:{color};">
      <div style="display:flex;align-items:center;gap:16px;">
        <div style="font-size:2.8rem;line-height:1">{icon}</div>
        <div>
          <div style="font-size:1.5rem;font-weight:800;color:{color};letter-spacing:1px">
            {band} RISK &nbsp;·&nbsp; {action}
          </div>
          <div style="color:#64748b;font-size:0.85rem;margin-top:4px">
            Score &nbsp;<b style="color:{color}">{result.risk_score:.0f}/100</b>
            &nbsp;·&nbsp; Confidence <b>{result.confidence*100:.0f}%</b>
            &nbsp;·&nbsp; <b>{result.processing_time_ms:.0f} ms</b>
            {"&nbsp;·&nbsp; <b style='color:#ff6b00'>⚠️ Coordinated Attack</b>" if result.is_coordinated_attack else ""}
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Charts
    g1, g2, g3 = st.columns([1, 1.1, 1])
    with g1:
        st.markdown("<p style='text-align:center;color:#64748b;font-size:0.75rem;letter-spacing:1px'>RISK GAUGE</p>", unsafe_allow_html=True)
        st.plotly_chart(gauge_fig(result.risk_score, band), use_container_width=True)
    with g2:
        st.markdown("<p style='color:#64748b;font-size:0.75rem;letter-spacing:1px'>MODULE BREAKDOWN</p>", unsafe_allow_html=True)
        render_module_bars(result.module_scores)
    with g3:
        st.markdown("<p style='text-align:center;color:#64748b;font-size:0.75rem;letter-spacing:1px'>RADAR VIEW</p>", unsafe_allow_html=True)
        if result.module_scores:
            st.plotly_chart(radar_fig(result.module_scores), use_container_width=True)

    # Explanation + factors
    e1, e2 = st.columns([2, 1])
    with e1:
        st.markdown(f"""
        <div class="trident-card">
          <div style="font-size:0.72rem;color:#64748b;letter-spacing:1px;margin-bottom:8px">AI EXPLANATION</div>
          <div style="line-height:1.75;color:#cbd5e1;font-size:0.9rem">{result.explanation}</div>
        </div>
        """, unsafe_allow_html=True)
    with e2:
        rows = "".join(
            f'<div style="padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:0.88rem;color:#94a3b8">'
            f'<span style="color:#00d4ff;font-weight:700;margin-right:8px">{i}.</span>{f}</div>'
            for i, f in enumerate(result.top_factors, 1)
        )
        st.markdown(f"""
        <div class="trident-card">
          <div style="font-size:0.72rem;color:#64748b;letter-spacing:1px;margin-bottom:8px">TOP RISK FACTORS</div>
          {rows}
        </div>
        """, unsafe_allow_html=True)

    if result.is_coordinated_attack:
        st.markdown(f"""
        <div style="background:#ff6b0012;border:1px solid #ff6b0044;border-radius:12px;padding:16px 20px;margin-top:4px">
          <b style="color:#ff6b00">⚠️ COORDINATED CAMPAIGN DETECTED</b><br>
          <span style="color:#94a3b8;font-size:0.88rem">{result.campaign_summary}</span>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("View raw JSON output"):
        st.json(result.model_dump())


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="padding:36px 0 24px;text-align:center;">
  <div style="font-size:0.75rem;letter-spacing:4px;color:#00d4ff;text-transform:uppercase;margin-bottom:8px">
    Barclays Hack-O-Hire · Theme 2
  </div>
  <div style="font-size:3.2rem;font-weight:800;letter-spacing:2px;
              background:linear-gradient(135deg,#ffffff,#00d4ff);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.1">
    ▾ TRIDENT
  </div>
  <div style="font-size:1rem;color:#64748b;margin-top:6px;letter-spacing:0.5px">
    AI-Fraud Detection Engine &nbsp;·&nbsp; 9 Independent Modules &nbsp;·&nbsp; Multi-Modal Analysis
  </div>
</div>
""", unsafe_allow_html=True)

# Module status strip
mod_info = [("🤖","AI Text"),("🔑","Credentials"),("🦠","Malware"),("💉","Injection"),
            ("📧","Phishing"),("🔗","URL"),("⚗️","Fusion"),("🕸️","Campaign"),("📊","SHAP")]
for col, (icon, name) in zip(st.columns(9), mod_info):
    col.markdown(f"""
    <div style="text-align:center;padding:8px 4px;background:rgba(0,212,255,0.05);
                border:1px solid rgba(0,212,255,0.1);border-radius:8px;font-size:0.72rem">
      <div style="font-size:1.1rem">{icon}</div>
      <div style="color:#64748b;margin-top:2px">{name}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

# ── Live alerts panel (poll via backend `/alerts`) ─────────────────────────────
ALERTS_API = os.environ.get("TRIDENT_ALERTS_URL", "http://127.0.0.1:8000/alerts")

_BAND_COLOR  = {"CRITICAL": "#ff0040", "HIGH": "#ff6b00", "MEDIUM": "#ffbf00", "LOW": "#00e676"}
_BAND_BG     = {"CRITICAL": "rgba(255,0,64,0.10)", "HIGH": "rgba(255,107,0,0.10)",
                "MEDIUM": "rgba(255,191,0,0.08)", "LOW": "rgba(0,230,118,0.07)"}
_BAND_ICON   = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "🔶", "LOW": "✅"}

def fetch_alerts(limit: int = 30):
    try:
        resp = requests.get(ALERTS_API, params={"limit": limit}, timeout=3)
        resp.raise_for_status()
        return resp.json().get("alerts", [])
    except Exception:
        return []

# Header row
_ac1, _ac2, _ac3 = st.columns([2, 2, 1])
with _ac1:
    st.markdown("### 📬 Processed Emails — Live Feed")
with _ac2:
    _filter_band = st.selectbox(
        "Filter by risk", ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"],
        label_visibility="collapsed"
    )
with _ac3:
    if st.button("⟳ Refresh"):
        st.rerun()

latest_alerts = fetch_alerts(30)
# Apply filter
_shown = [e for e in latest_alerts
          if _filter_band == "ALL" or (e.get("alert", {}).get("risk_band") == _filter_band)]

if not _shown:
    st.info("No emails processed yet — start the IMAP poller to see live results.")
else:
    # Summary badge row
    from collections import Counter
    _counts = Counter(e.get("alert", {}).get("risk_band", "?") for e in latest_alerts)
    _badge_html = " &nbsp; ".join(
        f'<span style="background:{_BAND_COLOR.get(b,"#888")};color:#000;'
        f'font-weight:700;padding:3px 10px;border-radius:20px;font-size:0.78rem">'
        f'{_BAND_ICON.get(b,"")} {b} {n}</span>'
        for b, n in [("CRITICAL", _counts["CRITICAL"]), ("HIGH", _counts["HIGH"]),
                     ("MEDIUM", _counts["MEDIUM"]), ("LOW", _counts["LOW"])] if n
    )
    st.markdown(_badge_html, unsafe_allow_html=True)
    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

    for entry in _shown:
        rec   = entry.get("alert", {})
        ts    = entry.get("received_at", "")[:19].replace("T", " ")
        subj  = rec.get("subject") or "(no subject)"
        sender= rec.get("sender") or "(unknown)"
        band  = rec.get("risk_band") or "?"
        score = rec.get("risk_score") or 0
        snippet = rec.get("snippet", "")[:180]
        action  = (rec.get("trident_result") or {}).get("recommended_action", "")
        top3    = (rec.get("trident_result") or {}).get("top_factors", [])
        col   = _BAND_COLOR.get(band, "#888")
        bg    = _BAND_BG.get(band, "rgba(255,255,255,0.04)")
        icon  = _BAND_ICON.get(band, "📧")

        st.markdown(f"""
<div style="background:{bg};border:1px solid {col}44;border-left:4px solid {col};
     border-radius:10px;padding:14px 18px;margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">
    <div style="font-weight:700;font-size:0.97rem;color:#e2e8f0">{icon} {subj}</div>
    <div>
      <span style="background:{col};color:#000;font-weight:800;padding:2px 10px;
            border-radius:12px;font-size:0.8rem">{band}</span>
      <span style="background:rgba(255,255,255,0.08);color:#e2e8f0;padding:2px 10px;
            border-radius:12px;font-size:0.8rem;margin-left:6px">⚡ {score:.1f}/100</span>
      {"<span style='background:rgba(255,255,255,0.08);color:#94a3b8;padding:2px 10px;border-radius:12px;font-size:0.8rem;margin-left:6px'>" + action + "</span>" if action else ""}
    </div>
  </div>
  <div style="color:#64748b;font-size:0.82rem;margin-top:5px">
    📨 {sender} &nbsp;·&nbsp; 🕐 {ts}
  </div>
  {"<div style='color:#94a3b8;font-size:0.83rem;margin-top:6px;font-style:italic'>" + snippet + "…</div>" if snippet else ""}
  {"<div style='margin-top:7px;font-size:0.8rem;color:#64748b'>🔍 " + " &nbsp;|&nbsp; ".join(top3) + "</div>" if top3 else ""}
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_demo, tab_email, tab_url, tab_full = st.tabs([
    "🚀  Demo Attack",
    "📧  Email Analysis",
    "🔗  URL Checker",
    "🎯  Full Detection",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — DEMO ATTACK
# ─────────────────────────────────────────────────────────────────────────────
with tab_demo:
    st.markdown("""
    <div class="trident-card" style="border-color:rgba(255,107,0,0.25);background:rgba(255,107,0,0.04)">
      <div style="font-size:0.72rem;letter-spacing:1px;color:#ff6b00;margin-bottom:10px">LIVE SCENARIO</div>
      <b style="color:#e2e8f0">Coordinated Multi-Channel Fraud Attack</b>
      <div style="color:#64748b;font-size:0.88rem;margin-top:8px;line-height:1.7">
        A victim receives a phishing email from
        <code style="color:#00d4ff">noreply@barclays-secure.xyz</code> —
        AI-written, containing exposed credentials, pointing to a lookalike banking site
        <code style="color:#ff0040">http://fake-bank.xyz</code> with a malicious
        <code style="color:#ff0040">invoice.exe</code> attachment.
        All signals originate from the same attacker infrastructure.
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="trident-card">
          <div style="font-size:0.72rem;letter-spacing:1px;color:#64748b;margin-bottom:8px">📧 EMAIL (AI-WRITTEN)</div>
          <div style="font-size:0.85rem;color:#94a3b8;line-height:1.7">
            <i>"I trust this finds you well. Your Barclays account has been flagged
            for suspicious activity and requires immediate verification. Please be
            advised that failure to comply will result in account suspension.
            <span style="color:#ffbf00">password=Bank@123!</span> Click the link
            below to secure your account immediately."</i>
          </div>
          <div style="margin-top:10px;font-size:0.78rem;color:#64748b">
            From: <span style="color:#00d4ff">noreply@barclays-secure.xyz</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="trident-card">
          <div style="font-size:0.72rem;letter-spacing:1px;color:#64748b;margin-bottom:8px">⚡ ATTACK VECTORS</div>
          <div style="font-size:0.85rem;line-height:2.1">
            <div>🔗 <span style="color:#64748b">URL:</span>
              <code style="color:#ff0040">http://fake-bank.xyz/verify</code></div>
            <div>📎 <span style="color:#64748b">File:</span>
              <code style="color:#ff0040">invoice.exe</code> (PE binary — MZ header)</div>
            <div>🔑 <span style="color:#64748b">Credential:</span>
              <code style="color:#ffbf00">password=Bank@123!</code> exposed in body</div>
            <div>🤖 <span style="color:#64748b">Origin:</span>
              <span style="color:#a78bfa">ChatGPT-style phrasing detected</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin:4px 0 12px'></div>", unsafe_allow_html=True)

    if st.button("▶  Run Demo Attack", key="btn_demo"):
        demo_email = (
            "I trust this finds you well. Your Barclays account has been flagged for "
            "suspicious activity and requires immediate verification. Please be advised "
            "that failure to comply will result in account suspension. "
            "password=Bank@123! Click the link below to secure your account immediately."
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".exe", prefix="invoice_") as tmp:
            tmp.write(b"MZ\x90\x00" + b"\x00" * 100)
            tmp_path = tmp.name

        with st.spinner("Running TRIDENT detection pipeline across all 9 modules…"):
            from core.data_models import FraudSignal
            t = load_trident()
            t.reset_graph()
            result = t.detect_fraud(FraudSignal(
                email_text=demo_email,
                email_subject="URGENT: Your Barclays Account Has Been Compromised",
                sender="noreply@barclays-secure.xyz",
                url="http://fake-bank.xyz/verify",
                attachment_path=tmp_path,
            ))
        try: os.unlink(tmp_path)
        except: pass
        display_result(result)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — EMAIL ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
with tab_email:
    c1, c2 = st.columns([3, 1])
    with c1:
        email_text = st.text_area("Email body", height=160,
                                  placeholder="Paste the full email body here…", key="email_body")
    with c2:
        email_subj = st.text_input("Subject", key="email_subj", placeholder="Optional")
        email_from = st.text_input("Sender",  key="email_from", placeholder="user@domain.com")

    if st.button("Analyse Email", key="btn_email"):
        if not email_text.strip():
            st.warning("Please enter email text.")
        else:
            with st.spinner("Analysing email across 6 modules…"):
                from core.data_models import FraudSignal
                t = load_trident()
                result = t.detect_fraud(FraudSignal(
                    email_text=email_text,
                    email_subject=email_subj or None,
                    sender=email_from or None,
                ))
            display_result(result)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — URL CHECKER
# ─────────────────────────────────────────────────────────────────────────────
with tab_url:
    url_in = st.text_input("URL to check", placeholder="http://example.com/path", key="url_check")

    if st.button("Check URL", key="btn_url"):
        if not url_in.strip():
            st.warning("Please enter a URL.")
        else:
            with st.spinner("Analysing URL…"):
                r = load_trident().url_detect.detect_malicious(url_in)

            prob  = r.get("malicious_probability", 0)
            risk  = r.get("risk", "LOW")
            color = RISK_COLORS.get(risk, "#888")

            st.markdown(f"""
            <div class="trident-card" style="border-color:{color}44">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                  <div style="font-size:1.4rem;font-weight:700;color:{color}">{risk}</div>
                  <div style="color:#64748b;font-size:0.85rem">Malicious probability:
                    <b style="color:{color}">{prob:.0f}%</b></div>
                  <div style="color:#475569;font-size:0.8rem;margin-top:8px;
                              font-family:'JetBrains Mono',monospace">{url_in}</div>
                </div>
                <div style="font-size:3rem;opacity:0.4">🔗</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            inds = r.get("indicators", [])
            if inds:
                ind_html = "".join(
                    f'<div style="padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.05);'
                    f'color:#94a3b8;font-size:0.85rem">• {i}</div>' for i in inds
                )
                st.markdown(f'<div class="trident-card">'
                            f'<div style="font-size:0.72rem;letter-spacing:1px;color:#64748b;margin-bottom:8px">INDICATORS</div>'
                            f'{ind_html}</div>', unsafe_allow_html=True)

            fig_url = go.Figure(go.Indicator(
                mode="gauge+number", value=prob,
                number={"font":{"color":color},"suffix":"%"},
                gauge={"axis":{"range":[0,100],"tickfont":{"color":"#64748b"}},
                       "bar":{"color":color},"bgcolor":"rgba(0,0,0,0)","borderwidth":0,
                       "steps":[{"range":[0,100],"color":"rgba(255,255,255,0.03)"}]},
            ))
            fig_url.update_layout(height=180, margin=dict(l=20,r=20,t=10,b=10),
                                  paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
            st.plotly_chart(fig_url, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — FULL DETECTION
# ─────────────────────────────────────────────────────────────────────────────
with tab_full:
    st.markdown("<div style='color:#64748b;font-size:0.88rem;margin-bottom:16px'>"
                "Combine email + URL + file for complete multi-modal analysis.</div>",
                unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        full_email  = st.text_area("Email body", height=140, key="full_email")
        full_sender = st.text_input("Sender", key="full_sender")
    with cb:
        full_url  = st.text_input("URL", key="full_url")
        full_file = st.file_uploader("Attachment", key="full_file",
                                     help="EXE, PDF, DOCX, etc.")

    if st.button("Run Full Analysis", key="btn_full"):
        if not any([full_email.strip(), full_url.strip(), full_file]):
            st.warning("Please provide at least one input.")
        else:
            att_path = None
            if full_file:
                ext = os.path.splitext(full_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(full_file.read()); att_path = tmp.name
            with st.spinner("Running full TRIDENT analysis…"):
                from core.data_models import FraudSignal
                t = load_trident()
                result = t.detect_fraud(FraudSignal(
                    email_text=full_email or None,
                    sender=full_sender or None,
                    url=full_url or None,
                    attachment_path=att_path,
                ))
            if att_path:
                try: os.unlink(att_path)
                except: pass
            display_result(result)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:48px;padding:16px 0;
            border-top:1px solid rgba(255,255,255,0.05);
            font-size:0.75rem;color:#334155;letter-spacing:1px">
  TRIDENT &nbsp;·&nbsp; AI-Fraud Detection Engine &nbsp;·&nbsp;
  Barclays Hack-O-Hire 2026 &nbsp;·&nbsp; All 9 modules built from scratch
</div>
""", unsafe_allow_html=True)
