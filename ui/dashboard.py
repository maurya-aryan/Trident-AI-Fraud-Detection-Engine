"""
TRIDENT — AI Fraud Detection Dashboard
Apple-Grade Design with Wave Hero, Liquid Glass, Scroll Animations, Edge-Only Spotlight.
Run: streamlit run UI/dashboard.py
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
    page_title="TRIDENT | Enterprise Fraud Detection",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

:root {
    --bg-void:       #020810;
    --bg-deep:       #030d1a;
    --bg-glass:      rgba(3, 13, 28, 0.55);
    --bg-glass-2:    rgba(5, 18, 36, 0.70);
    --bg-header:     rgba(2, 8, 16, 0.72);

    --sea-1:  #0a3d5c;
    --sea-2:  #0c4f78;
    --sea-3:  #0d6090;
    --wave-foam: rgba(180, 220, 255, 0.12);

    --text-main:     #dff0fb;
    --text-muted:    #6fa8c9;
    --text-faint:    #254e6a;
    --text-accent:   #5bc4ef;

    --border-dim:    rgba(11, 110, 170, 0.14);
    --border-mid:    rgba(14, 150, 210, 0.28);
    --border-glow:   rgba(14, 165, 233, 0.9);

    --risk-crit:  #EF4444;
    --risk-high:  #F97316;
    --risk-med:   #EAB308;
    --risk-low:   #10B981;

    --gold:       #c8a84b;
    --gold-light: rgba(200, 168, 75, 0.15);

    --font-display: 'Cormorant Garamond', serif;
    --font-ui:      'Space Grotesk', sans-serif;
    --font-mono:    'JetBrains Mono', monospace;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background-color: var(--bg-void) !important;
    color: var(--text-main);
    font-family: var(--font-ui);
    overflow-x: hidden;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none; }

.block-container {
    padding-top: 0 !important;
    max-width: 1100px;
    position: relative;
    z-index: 10;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(14, 165, 233, 0.22); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(14, 165, 233, 0.5); }

/* ──────────────────────────────────────────────────
   FLOATING HEADER — LIQUID GLASS PILL
   ────────────────────────────────────────────────── */
.floating-header {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: min(820px, calc(100% - 40px));
    height: 52px;
    z-index: 9999;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 26px;
    border-radius: 999px;
    /* Liquid Glass */
    background: rgba(2, 10, 22, 0.55);
    backdrop-filter: blur(32px) saturate(200%) brightness(1.05);
    -webkit-backdrop-filter: blur(32px) saturate(200%) brightness(1.05);
    border: 1px solid rgba(11, 130, 200, 0.18);
    box-shadow:
        0 2px 0 rgba(255,255,255,0.04) inset,
        0 -1px 0 rgba(0,0,0,0.6) inset,
        0 8px 32px rgba(0,0,0,0.6),
        0 0 0 0.5px rgba(14, 165, 233, 0.08);
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1),
                opacity 0.4s ease,
                background 0.3s ease;
    /* Rainbow-sheen shimmer on top edge */
    overflow: hidden;
}

.floating-header::before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: linear-gradient(
        135deg,
        rgba(255,255,255,0.04) 0%,
        transparent 40%,
        rgba(14, 165, 233, 0.05) 60%,
        transparent 100%
    );
    pointer-events: none;
}

/* Top specular line */
.floating-header::after {
    content: "";
    position: absolute;
    top: 0; left: 12px; right: 12px;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), rgba(14, 165, 233, 0.2), rgba(255,255,255,0.12), transparent);
    border-radius: 1px;
    pointer-events: none;
}

.header-logo {
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.25rem;
    letter-spacing: 5px;
    color: var(--text-main);
    text-transform: uppercase;
}

.header-nav {
    display: flex;
    align-items: center;
    gap: 28px;
}

.header-nav-item {
    font-family: var(--font-ui);
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-muted);
    cursor: default;
    transition: color 0.2s ease;
}
.header-nav-item:hover { color: var(--text-main); }

.header-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: var(--font-mono);
    font-size: 0.65rem;
    font-weight: 500;
    color: var(--text-muted);
    letter-spacing: 1px;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; box-shadow: 0 0 5px rgba(14,165,233,0.6); }
    50% { opacity: 0.6; box-shadow: 0 0 12px rgba(14,165,233,1); background: #5bc4ef; }
}
.status-dot {
    width: 5px; height: 5px;
    background: #0EA5E9;
    border-radius: 50%;
    animation: pulse-dot 3s infinite;
}

/* ──────────────────────────────────────────────────
   HERO SECTION
   ────────────────────────────────────────────────── */
.hero-section {
    position: relative;
    width: 100vw;
    left: 50%; right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
    height: 100vh;
    min-height: 600px;
    overflow: hidden;
    margin-bottom: 0;
}

/* The painting itself */
.hero-painting {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(to bottom,
            rgba(2, 8, 16, 0.08) 0%,
            rgba(2, 8, 16, 0.0) 40%,
            rgba(2, 8, 16, 0.72) 85%,
            rgba(2, 8, 16, 1) 100%
        ),
        url('https://images.unsplash.com/photo-1518182170546-076616fdca44?q=80&w=2400&auto=format&fit=crop&ixlib=rb-4.0.3');
    background-size: cover;
    background-position: center 35%;
    transform: scale(1.06) translateX(0);
    transform-origin: center;
    will-change: transform;
    transition: transform 0.1s linear;
}

/* Colour-grade the painting dark-ocean */
.hero-painting::after {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(180deg, rgba(0, 40, 80, 0.30) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 90%, rgba(0, 20, 50, 0.5) 0%, transparent 70%);
    mix-blend-mode: multiply;
}

/* Hero Title */
.hero-title-wrap {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    z-index: 4;
    pointer-events: none;
}

.hero-title {
    font-family: var(--font-display);
    font-size: clamp(6rem, 14vw, 11rem);
    font-weight: 300;
    letter-spacing: 0.25em;
    color: rgba(255, 255, 255, 0.94);
    text-transform: uppercase;
    line-height: 1;
    text-shadow:
        0 0 80px rgba(10, 90, 160, 0.8),
        0 4px 40px rgba(0,0,0,0.7);
    opacity: 0;
    transform: translateY(18px);
    animation: hero-in 2s cubic-bezier(0.16, 1, 0.3, 1) 0.3s forwards;
}

@keyframes hero-in {
    to { opacity: 1; transform: translateY(0); }
}

.hero-tagline {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 4px;
    color: rgba(100, 180, 230, 0.8);
    text-transform: uppercase;
    margin-top: 20px;
    opacity: 0;
    animation: hero-in 1.5s ease 0.9s forwards;
}

/* Scroll indicator */
.hero-scroll-hint {
    position: absolute;
    bottom: 36px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 5;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    opacity: 0;
    animation: hero-in 1s ease 1.8s forwards;
}
.scroll-line {
    width: 1px;
    height: 40px;
    background: linear-gradient(to bottom, rgba(14, 165, 233, 0.6), transparent);
    animation: scroll-line 2s ease-in-out infinite;
}
@keyframes scroll-line {
    0%, 100% { transform: scaleY(1); opacity: 0.7; }
    50% { transform: scaleY(0.5); opacity: 0.3; }
}
.scroll-label {
    font-family: var(--font-mono);
    font-size: 0.58rem;
    letter-spacing: 3px;
    color: rgba(100, 170, 210, 0.6);
}

/* Wave sweep on scroll */
.hero-painting.wave-swept {
    animation: wave-sweep 1.4s cubic-bezier(0.77, 0, 0.175, 1) forwards;
}
@keyframes wave-sweep {
    0%   { clip-path: inset(0 0 0 0); }
    100% { clip-path: inset(0 0 0 100%); }
}

/* ──────────────────────────────────────────────────
   WAVE REVEAL ANIMATION (scroll-triggered)
   ────────────────────────────────────────────────── */
.wave-reveal {
    opacity: 0;
    transform: translateY(28px);
    transition:
        opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1),
        transform 0.9s cubic-bezier(0.16, 1, 0.3, 1);
    will-change: opacity, transform;
}
.wave-reveal.in-view {
    opacity: 1;
    transform: translateY(0);
}

/* ──────────────────────────────────────────────────
   OCEAN AMBIENT BACKGROUND (post-hero)
   ────────────────────────────────────────────────── */
.ocean-ambient {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

/* Slow moving deep-sea blobs */
.ambient-blob {
    position: absolute;
    border-radius: 50%;
    filter: blur(90px);
    opacity: 0;
    transition: opacity 2s ease;
}
.ambient-blob.visible { opacity: 1; }

.blob-1 {
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(0, 60, 120, 0.18) 0%, transparent 70%);
    top: 30%; left: -10%;
    animation: blob-drift-1 28s ease-in-out infinite;
}
.blob-2 {
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(0, 40, 90, 0.14) 0%, transparent 70%);
    top: 60%; right: -8%;
    animation: blob-drift-2 22s ease-in-out infinite;
}
.blob-3 {
    width: 700px; height: 350px;
    background: radial-gradient(ellipse, rgba(10, 70, 140, 0.1) 0%, transparent 70%);
    top: 120%; left: 20%;
    animation: blob-drift-3 34s ease-in-out infinite;
}

@keyframes blob-drift-1 {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(40px, -30px) scale(1.05); }
    66% { transform: translate(-20px, 20px) scale(0.97); }
}
@keyframes blob-drift-2 {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(-50px, -40px) scale(1.08); }
}
@keyframes blob-drift-3 {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(30px, -20px); }
}

/* ──────────────────────────────────────────────────
   GLASS CARDS — EDGE-ONLY SPOTLIGHT
   ────────────────────────────────────────────────── */
.glass-card-wrapper {
    position: relative;
    border-radius: 16px;
    background: var(--bg-glass);
    backdrop-filter: blur(28px) saturate(160%);
    -webkit-backdrop-filter: blur(28px) saturate(160%);
    margin-bottom: 20px;
    padding: 24px;
    /* Layered glass effect */
    box-shadow:
        0 1px 0 rgba(255,255,255,0.04) inset,
        0 -1px 0 rgba(0,0,0,0.4) inset,
        0 12px 40px rgba(0,0,0,0.45),
        0 1px 1px rgba(0,0,0,0.2);
    transition:
        transform 0.5s cubic-bezier(0.16, 1, 0.3, 1),
        box-shadow 0.5s ease;
}

.glass-card-wrapper:hover {
    transform: translateY(-2px);
    box-shadow:
        0 1px 0 rgba(255,255,255,0.06) inset,
        0 -1px 0 rgba(0,0,0,0.5) inset,
        0 20px 60px rgba(0,0,0,0.55),
        0 0 0 0.5px rgba(14, 165, 233, 0.08);
}

/* Permanent dim border */
.glass-card-wrapper::before {
    content: "";
    position: absolute; inset: 0;
    border-radius: inherit;
    border: 1px solid var(--border-dim);
    pointer-events: none;
    z-index: 1;
}

/* Edge-only spotlight — ONLY activates at border */
.glass-card-wrapper::after {
    content: "";
    position: absolute; inset: 0;
    border-radius: 16px;
    padding: 1px;
    background: radial-gradient(
        300px circle at var(--mouse-x, -9999px) var(--mouse-y, -9999px),
        rgba(14, 165, 233, 0.85),
        transparent 50%
    );
    -webkit-mask:
        linear-gradient(#fff 0 0) content-box,
        linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.4s ease;
    z-index: 2;
}
.glass-card-wrapper:hover::after { opacity: 1; }

/* ── GOLD ACCENT CARD ── */
.glass-card-gold {
    background: linear-gradient(135deg,
        rgba(200, 168, 75, 0.06) 0%,
        rgba(3, 13, 28, 0.7) 50%
    );
    border-color: rgba(200, 168, 75, 0.15);
}
.glass-card-gold::before { border-color: rgba(200, 168, 75, 0.18); }

/* ──────────────────────────────────────────────────
   STATS STRIP
   ────────────────────────────────────────────────── */
.stat-pill {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 14px 8px;
    border-radius: 12px;
    background: rgba(3, 14, 30, 0.6);
    border: 1px solid rgba(11, 100, 160, 0.12);
    backdrop-filter: blur(20px);
    text-align: center;
    transition: background 0.3s ease, border-color 0.3s ease;
}
.stat-pill:hover {
    background: rgba(5, 20, 45, 0.75);
    border-color: rgba(14, 120, 180, 0.22);
}
.stat-name {
    font-family: var(--font-mono);
    font-size: 0.55rem;
    font-weight: 500;
    letter-spacing: 1.5px;
    color: var(--text-faint);
    text-transform: uppercase;
    margin-bottom: 6px;
}
.stat-value {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--text-accent);
    letter-spacing: 0.5px;
}

/* ──────────────────────────────────────────────────
   MODULE BARS
   ────────────────────────────────────────────────── */
.module-bar-row {
    margin-bottom: 14px;
}
.module-bar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.module-bar-label {
    font-family: var(--font-ui);
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--text-muted);
}
.module-bar-val {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    font-weight: 600;
}
.module-bar-track {
    height: 3px;
    background: rgba(14, 165, 233, 0.08);
    border-radius: 99px;
    overflow: hidden;
}
.module-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 1.4s cubic-bezier(0.16, 1, 0.3, 1);
}

/* ──────────────────────────────────────────────────
   TAB CONTROLS
   ────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    gap: 4px;
    background: rgba(2, 8, 18, 0.5);
    border-radius: 12px;
    padding: 6px;
    border: 1px solid var(--border-dim);
    backdrop-filter: blur(20px);
    margin-bottom: 32px;
    width: fit-content;
}
[data-testid="stTabs"] [role="tablist"]::-webkit-scrollbar { display: none; }

[data-testid="stTabs"] button[role="tab"] {
    border: none !important;
    background: transparent !important;
    color: var(--text-faint) !important;
    font-family: var(--font-ui) !important;
    font-weight: 500 !important;
    font-size: 0.75rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase;
    padding: 8px 20px !important;
    border-radius: 8px !important;
    transition: all 0.25s ease !important;
}
[data-testid="stTabs"] button[role="tab"]:hover {
    color: var(--text-main) !important;
    background: rgba(14, 165, 233, 0.05) !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: var(--text-main) !important;
    background: rgba(14, 165, 233, 0.1) !important;
    border: 1px solid rgba(14, 165, 233, 0.2) !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,0.04) inset,
        0 2px 8px rgba(0,0,0,0.3) !important;
}

/* ──────────────────────────────────────────────────
   BUTTONS
   ────────────────────────────────────────────────── */
[data-testid="stButton"] > button {
    font-family: var(--font-ui) !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase;
    background: rgba(5, 60, 100, 0.3) !important;
    color: var(--text-main) !important;
    border: 1px solid rgba(14, 165, 233, 0.35) !important;
    border-radius: 10px !important;
    padding: 11px 32px !important;
    backdrop-filter: blur(10px);
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stButton"] > button::before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, transparent 50%);
}
[data-testid="stButton"] > button:hover {
    background: rgba(14, 90, 160, 0.45) !important;
    border-color: rgba(14, 165, 233, 0.6) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(14, 90, 160, 0.35) !important;
}

/* ──────────────────────────────────────────────────
   INPUTS
   ────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] > div > div {
    font-family: var(--font-mono) !important;
    font-size: 0.83rem !important;
    background: rgba(1, 8, 18, 0.65) !important;
    border: 1px solid var(--border-dim) !important;
    color: var(--text-main) !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(14, 165, 233, 0.5) !important;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.08) !important;
    outline: none !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label {
    font-family: var(--font-ui) !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase;
    color: var(--text-muted) !important;
}

[data-testid="stExpander"] {
    background: var(--bg-glass) !important;
    border: 1px solid var(--border-dim) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(24px);
}
[data-testid="stExpander"] summary {
    font-family: var(--font-ui) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--text-main) !important;
}

/* ──────────────────────────────────────────────────
   UTILITY CLASSES
   ────────────────────────────────────────────────── */
.mono-text { font-family: var(--font-mono); font-size: 0.83rem; }
.label-text {
    font-family: var(--font-ui);
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    color: var(--text-muted);
}
.section-divider {
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-mid), transparent);
    margin: 48px 0;
}
</style>

<!-- ── Ocean ambient layer ── -->
<div class="ocean-ambient" id="ocean-ambient">
    <div class="ambient-blob blob-1"></div>
    <div class="ambient-blob blob-2"></div>
    <div class="ambient-blob blob-3"></div>
</div>

<!-- ── Floating header ── -->
<div class="floating-header" id="floating-header">
    <div class="header-logo">Trident</div>
    <div class="header-nav">
        <span class="header-nav-item">Overview</span>
        <span class="header-nav-item">Analysis</span>
        <span class="header-nav-item">Alerts</span>
    </div>
    <div class="header-status">
        <div class="status-dot"></div>
        SYSTEM ACTIVE
    </div>
</div>

<!-- ── Hero ── -->
<div class="hero-section" id="hero-section">
    <div class="hero-painting" id="hero-painting"></div>
    <div class="hero-title-wrap">
        <div class="hero-title">Trident</div>
        <div class="hero-tagline">Enterprise Fraud Detection Platform</div>
    </div>
    <div class="hero-scroll-hint">
        <div class="scroll-line"></div>
        <div class="scroll-label">Scroll</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Scroll & Interaction JS ───────────────────────────────────────────────────
components.html("""
<script>
(function(){
    const setup = () => {
        try {
            const doc = window.parent.document;

            // ── EDGE-ONLY spotlight on glass cards ──
            doc.addEventListener('mousemove', (e) => {
                doc.querySelectorAll('.glass-card-wrapper').forEach(el => {
                    const r = el.getBoundingClientRect();
                    el.style.setProperty('--mouse-x', `${e.clientX - r.left}px`);
                    el.style.setProperty('--mouse-y', `${e.clientY - r.top}px`);
                });
            });

            // ── Scroll Observer for wave-reveal elements ──
            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry, i) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('in-view');
                    }
                });
            }, { threshold: 0.06, rootMargin: '0px 0px -30px 0px' });

            // Continuously check for new elements
            const scanElements = () => {
                doc.querySelectorAll('.glass-card-wrapper:not(.observed), .stat-pill:not(.observed)').forEach((el, i) => {
                    el.classList.add('observed', 'wave-reveal');
                    el.style.transitionDelay = `${(i % 4) * 0.07}s`;
                    observer.observe(el);
                });
            };
            setInterval(scanElements, 400);

            // ── Hero painting parallax + sweep on scroll ──
            const painting = doc.getElementById('hero-painting');
            const ambient = doc.querySelectorAll('.ambient-blob');

            let swept = false;
            let lastScroll = 0;
            const header = doc.getElementById('floating-header');

            doc.addEventListener('scroll', () => {
                const sy = doc.documentElement.scrollTop || doc.body.scrollTop;
                const winH = window.parent.innerHeight;

                // Parallax on painting
                if (painting && sy < winH) {
                    const p = sy / winH;
                    painting.style.transform = `scale(1.06) translateY(${p * 60}px)`;
                }

                // Wave sweep when scrolled past 60% of viewport
                if (painting && !swept && sy > winH * 0.55) {
                    swept = true;
                    painting.classList.add('wave-swept');
                    // Show ambient blobs
                    ambient.forEach(b => b.classList.add('visible'));
                } else if (swept && sy < winH * 0.3) {
                    swept = false;
                    painting.classList.remove('wave-swept');
                }

                // Hide / show floating header
                if (header) {
                    if (sy > lastScroll && sy > 220) {
                        header.style.transform = 'translateX(-50%) translateY(-88px)';
                    } else {
                        header.style.transform = 'translateX(-50%) translateY(0)';
                    }
                }
                lastScroll = sy <= 0 ? 0 : sy;
            }, { passive: true });

            // ── Animated wave at section transitions ──
            // We inject a subtle particle canvas at the boundary
            const injectWaveCanvas = () => {
                if (doc.getElementById('wave-canvas')) return;
                const canvas = doc.createElement('canvas');
                canvas.id = 'wave-canvas';
                Object.assign(canvas.style, {
                    position: 'fixed',
                    bottom: '0',
                    left: '0',
                    width: '100%',
                    height: '80px',
                    pointerEvents: 'none',
                    zIndex: '1',
                    opacity: '0.35',
                });
                doc.body.appendChild(canvas);

                const ctx = canvas.getContext('2d');
                let frame = 0;

                const drawWave = () => {
                    canvas.width = doc.body.clientWidth;
                    canvas.height = 80;
                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    for (let w = 0; w < 3; w++) {
                        ctx.beginPath();
                        ctx.moveTo(0, 80);
                        const offset = frame * (0.012 - w * 0.003);
                        const amp = 12 - w * 3;
                        for (let x = 0; x <= canvas.width; x += 4) {
                            const y = 40 + Math.sin(x / 90 + offset) * amp +
                                       Math.sin(x / 50 + offset * 1.3) * (amp * 0.4);
                            x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
                        }
                        ctx.lineTo(canvas.width, 80);
                        ctx.closePath();
                        ctx.fillStyle = `rgba(10, 70, 130, ${0.07 - w * 0.02})`;
                        ctx.fill();
                    }

                    frame++;
                    requestAnimationFrame(drawWave);
                };
                drawWave();
            };

            setTimeout(injectWaveCanvas, 600);

        } catch(e) {}
    };
    setTimeout(setup, 500);
})();
</script>
""", height=0, scrolling=False)


# ── Cached TRIDENT ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="INITIALISING ENGINE...")
def load_trident():
    from core.trident import TRIDENT
    return TRIDENT()

# ── Constants & helpers ───────────────────────────────────────────────────────
RISK_COLORS  = {"CRITICAL":"#EF4444","HIGH":"#F97316","MEDIUM":"#EAB308","LOW":"#10B981"}
ACTION_LABELS = {"BLOCK":"[ BLOCK ]","ESCALATE":"[ ESCALATE ]","WARN":"[ WARN ]","VERIFY":"[ VERIFY ]"}
MODULE_LABELS = {
    "ai_text_score":        "AI Generator",
    "credential_score":     "Credential Exposure",
    "malware_score":        "File Threat",
    "email_phishing_score": "Phishing Topology",
    "url_score":            "URL Reputation",
    "injection_score":      "Prompt Injection",
}

def bar_color(v):
    return "#EF4444" if v>=75 else "#F97316" if v>=50 else "#EAB308" if v>=25 else "#10B981"

def render_module_bars(scores: dict):
    html = ""
    for key, label in MODULE_LABELS.items():
        v = scores.get(key, 0)
        c = bar_color(v)
        html += f"""
        <div class="module-bar-row">
          <div class="module-bar-header">
            <span class="module-bar-label">{label}</span>
            <span class="module-bar-val" style="color:{c};">{v:.0f}</span>
          </div>
          <div class="module-bar-track">
            <div class="module-bar-fill" style="width:{v}%; background:{c}; box-shadow: 0 0 8px {c}66;"></div>
          </div>
        </div>"""
    st.markdown(
        f'<div class="glass-card-wrapper">{html}</div>',
        unsafe_allow_html=True
    )

def gauge_fig(score, band, height=200):
    color = RISK_COLORS.get(band, "#888888")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"font":{"size":40,"color":color,"family":"Space Grotesk","weight":"bold"},"suffix":""},
        gauge={
            "axis":{"range":[0,100],"tickwidth":0,"tickcolor":"rgba(0,0,0,0)","showticklabels": False},
            "bar":{"color":color,"thickness":0.05},
            "bgcolor":"rgba(14, 165, 233, 0.04)",
            "borderwidth":0,
            "threshold":{"line":{"color":color,"width":3},"thickness":0.1,"value":score},
        },
    ))
    fig.update_layout(
        height=height, margin=dict(l=20,r=20,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Space Grotesk"
    )
    return fig

def radar_fig(scores: dict):
    labels = [MODULE_LABELS.get(k,k) for k in scores]
    values = list(scores.values())
    labels.append(labels[0]); values.append(values[0])
    fig = go.Figure(go.Scatterpolar(
        r=values, theta=labels, fill='toself',
        fillcolor='rgba(14, 165, 233, 0.07)',
        line=dict(color='rgba(14, 165, 233, 0.7)', width=1.5),
        marker=dict(size=5, color='#0EA5E9', symbol='circle'),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=False, range=[0,100]),
            angularaxis=dict(
                tickfont=dict(color="rgba(100, 170, 210, 0.6)", size=8, family="Space Grotesk"),
                gridcolor="rgba(14, 165, 233, 0.08)",
                linecolor="rgba(14, 165, 233, 0.08)"
            ),
        ),
        height=220, margin=dict(l=40,r=40,t=20,b=20),
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
    )
    return fig

# ── Result renderer ───────────────────────────────────────────────────────────
def display_result(result):
    band   = result.risk_band
    action = result.recommended_action
    color  = RISK_COLORS.get(band, "#888888")
    label  = ACTION_LABELS.get(action, "[ UNKNOWN ]")

    st.markdown(f"""
    <div class="glass-card-wrapper" style="border-left: 2px solid {color}66; margin-top: 24px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap: 24px;">
          <div>
            <div class="label-text" style="margin-bottom:10px;">Detection Result</div>
            <div style="font-family:var(--font-display); font-size:2.8rem; font-weight:500; color:{color}; letter-spacing:2px; margin-bottom:14px; text-shadow: 0 0 30px {color}44; line-height:1;">
              {band}
            </div>
            <div style="font-family:var(--font-mono); font-size:0.8rem; color:var(--text-main); margin-bottom:6px; font-weight:500;">
              Score — <span style="color:{color}; font-weight:700;">{result.risk_score:.1f}/100</span>
            </div>
            <div style="font-family:var(--font-mono); font-size:0.7rem; color:var(--text-muted);">
              Confidence {result.confidence*100:.0f}% &nbsp;&middot;&nbsp; {result.processing_time_ms:.0f}ms
            </div>
          </div>
          <div style="text-align:right; flex-shrink:0;">
             <div style="font-family:var(--font-mono); color:{color}; font-weight:600; font-size:0.75rem;
                         padding:8px 18px; border:1px solid {color}44; border-radius:8px; display:inline-block;
                         background:{color}0d; letter-spacing:1px;">
                {label}
             </div>
             {"<div style='margin-top:14px; color:#F97316; font-size:0.68rem; font-family:var(--font-mono); font-weight:600; letter-spacing:1px;'>COORDINATED ATTACK</div>" if result.is_coordinated_attack else ""}
          </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    g1, g2, g3 = st.columns([1, 1.2, 1])
    with g1:
        st.markdown("<div class='label-text' style='text-align:center; margin-bottom:10px;'>Risk Metric</div>", unsafe_allow_html=True)
        st.plotly_chart(gauge_fig(result.risk_score, band), use_container_width=True)
    with g2:
        st.markdown("<div class='label-text' style='margin-bottom:10px;'>Subsystem Analysis</div>", unsafe_allow_html=True)
        render_module_bars(result.module_scores)
    with g3:
        st.markdown("<div class='label-text' style='text-align:center; margin-bottom:10px;'>Vector Map</div>", unsafe_allow_html=True)
        if result.module_scores:
            st.plotly_chart(radar_fig(result.module_scores), use_container_width=True)

    e1, e2 = st.columns([1.5, 1])
    with e1:
        st.markdown(f"""
        <div class="glass-card-wrapper">
            <div class="label-text" style="margin-bottom:16px;">Intelligence Summary</div>
            <div style="line-height:1.85; color:rgba(224, 242, 254, 0.85); font-size:0.92rem; font-family:var(--font-ui); font-weight:400;">
              {result.explanation}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with e2:
        rows = "".join(
            f'<div style="padding:11px 0; border-bottom:1px solid rgba(11,110,170,0.12); display:flex; gap:14px; align-items:center;">'
            f'<span style="font-family:var(--font-mono); font-size:0.65rem; color:rgba(14,165,233,0.5); font-weight:700; width:18px; flex-shrink:0;">0{i}</span>'
            f'<span style="color:var(--text-main); font-size:0.83rem; font-weight:400; font-family:var(--font-ui);">{f}</span></div>'
            for i, f in enumerate(result.top_factors, 1)
        )
        st.markdown(f"""
        <div class="glass-card-wrapper">
            <div class="label-text" style="margin-bottom:10px;">Key Indicators</div>
            {rows}
        </div>
        """, unsafe_allow_html=True)

    if result.is_coordinated_attack:
        st.markdown(f"""
        <div class="glass-card-wrapper" style="border-left: 2px solid rgba(249,115,22,0.5);">
            <div class="label-text" style="color:#F97316; margin-bottom:10px;">Campaign Correlation</div>
            <div style="color:var(--text-muted); font-size:0.88rem; line-height:1.7; font-family:var(--font-ui);">
              {result.campaign_summary}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("RAW TELEMETRY"):
        st.json(result.model_dump())


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='margin-top: 48px'></div>", unsafe_allow_html=True)

# Module status strip
mod_info = ["AI TEXT", "CREDENTIAL", "MALWARE", "INJECTION", "PHISHING", "URL", "FUSION", "CAMPAIGN", "SHAP"]
cols = st.columns(9)
for col, name in zip(cols, mod_info):
    col.markdown(f"""
    <div class="stat-pill">
        <div class="stat-name">{name}</div>
        <div class="stat-value">ACTIVE</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:56px'></div>", unsafe_allow_html=True)

# ── Live alerts panel ─────────────────────────────────────────────────────────
ALERTS_API = os.environ.get("TRIDENT_ALERTS_URL", "http://127.0.0.1:8000/alerts")
_BAND_COLOR = {"CRITICAL":"#EF4444","HIGH":"#F97316","MEDIUM":"#EAB308","LOW":"#10B981"}

def fetch_alerts(limit: int = 30):
    try:
        resp = requests.get(ALERTS_API, params={"limit": limit}, timeout=3)
        resp.raise_for_status()
        return resp.json().get("alerts", [])
    except Exception:
        return []

_ac1, _ac2, _ac3 = st.columns([2, 2, 1])
with _ac1:
    st.markdown("<div class='label-text' style='padding-top:12px; font-size:0.62rem;'>Live Ingestion Feed</div>", unsafe_allow_html=True)
with _ac2:
    _filter_band = st.selectbox("FILTER", ["ALL","CRITICAL","HIGH","MEDIUM","LOW"], label_visibility="collapsed")
with _ac3:
    if st.button("REFRESH"): st.rerun()

latest_alerts = fetch_alerts(30)
_shown = [e for e in latest_alerts if _filter_band == "ALL" or (e.get("alert", {}).get("risk_band") == _filter_band)]

if not _shown:
    st.markdown("""
    <div class="glass-card-wrapper" style="text-align:center; padding: 40px;">
        <div style="color:var(--text-faint); font-size:0.8rem; font-weight:500; font-family:var(--font-mono); letter-spacing:2px;">
            SYSTEM IDLE — AWAITING TELEMETRY
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    from collections import Counter
    _counts = Counter(e.get("alert", {}).get("risk_band", "?") for e in latest_alerts)
    _badge_html = " ".join(
        f'<span style="color:{_BAND_COLOR.get(b,"#888")}; font-family:var(--font-mono); font-weight:600; margin-right:14px; font-size:0.7rem; letter-spacing:0.5px;">{b} <span style="opacity:0.6;">{n}</span></span>'
        for b, n in [("CRITICAL",_counts["CRITICAL"]),("HIGH",_counts["HIGH"]),("MEDIUM",_counts["MEDIUM"]),("LOW",_counts["LOW"])] if n
    )
    st.markdown(f"<div style='margin-bottom:18px; padding-bottom:18px; border-bottom: 1px solid var(--border-dim);'>{_badge_html}</div>", unsafe_allow_html=True)

    for entry in _shown:
        rec     = entry.get("alert", {})
        ts      = entry.get("received_at", "")[:19].replace("T", " ")
        subj    = rec.get("subject") or "UNTITLED_RECORD"
        sender  = rec.get("sender") or "UNKNOWN_SENDER"
        band    = rec.get("risk_band") or "UNKNOWN"
        score   = rec.get("risk_score") or 0
        snippet = rec.get("snippet", "")[:120]
        col     = _BAND_COLOR.get(band, "#888")

        st.markdown(f"""
        <div class="glass-card-wrapper" style="border-left: 2px solid {col}44; padding: 20px 24px;">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:12px;">
              <div style="font-family:var(--font-ui); font-weight:500; font-size:0.92rem; color:var(--text-main);">
                {subj}
              </div>
              <div style="flex-shrink:0;">
                <span style="color:{col}; font-family:var(--font-mono); font-weight:600; font-size:0.7rem;
                             background:{col}0d; padding:4px 10px; border-radius:6px; border:1px solid {col}33; letter-spacing:0.5px;">
                    {band} &middot; {score:.1f}
                </span>
              </div>
            </div>
            <div style="font-family:var(--font-mono); color:var(--text-faint); font-size:0.67rem; margin-top:8px; font-weight:500; letter-spacing:0.5px;">
              {sender} &nbsp;&middot;&nbsp; {ts}
            </div>
            {"<div style='color:var(--text-muted); font-size:0.83rem; margin-top:10px; line-height:1.55; font-family:var(--font-ui); font-weight:400; opacity:0.8;'>" + snippet + "…</div>" if snippet else ""}
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

tab_demo, tab_email, tab_url, tab_full = st.tabs([
    "Demo Attack",
    "Email Analysis",
    "URL Checker",
    "Full Detection",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — DEMO ATTACK
# ─────────────────────────────────────────────────────────────────────────────
with tab_demo:
    st.markdown("""
    <div class="glass-card-wrapper glass-card-gold" style="border-left: 2px solid rgba(200,168,75,0.3);">
        <div class="label-text" style="color:var(--gold); margin-bottom:12px;">Simulated Scenario</div>
        <div style="font-family:var(--font-ui); font-size:1.12rem; color:var(--text-main); font-weight:600; margin-bottom:12px; letter-spacing:-0.2px;">
          Coordinated Multi-Channel Fraud Injection
        </div>
        <div style="color:var(--text-muted); font-size:0.9rem; line-height:1.7; font-family:var(--font-ui);">
          Targeted phishing operation via
          <span style="font-family:var(--font-mono); color:var(--text-accent); font-weight:600; font-size:0.82rem;">noreply@secure-bank.xyz</span>.
          Contains AI-generated payload, exposed credentials, and malicious redirection to
          <span style="font-family:var(--font-mono); color:var(--text-accent); font-weight:600; font-size:0.82rem;">http://fake-bank.xyz</span> harboring
          <span style="font-family:var(--font-mono); color:var(--text-accent); font-weight:600; font-size:0.82rem;">invoice.exe</span>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="glass-card-wrapper">
            <div class="label-text" style="margin-bottom:16px;">Payload Transcript</div>
            <div style="font-size:0.88rem; color:var(--text-muted); line-height:1.85; font-style:italic; font-family:var(--font-ui);">
              "I trust this finds you well. Your account has been flagged
              for suspicious activity and requires immediate verification.
              <span style="color:#EF4444; font-family:var(--font-mono); font-style:normal; font-weight:600; background:rgba(239, 68, 68, 0.08); padding:1px 5px; border-radius:4px; border: 1px solid rgba(239,68,68,0.2);">password=Bank@123!</span>
              Click the link below to secure your account immediately."
            </div>
            <div style="font-family:var(--font-mono); margin-top:18px; font-size:0.67rem; color:var(--text-faint); letter-spacing:0.5px;">
              SRC — <span style="color:var(--text-muted)">noreply@secure-bank.xyz</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="glass-card-wrapper">
            <div class="label-text" style="margin-bottom:16px;">Vector Identifiers</div>
            <div style="font-family:var(--font-mono); font-size:0.8rem; line-height:1;">
              <div style="border-bottom: 1px solid rgba(11,100,160,0.12); padding:12px 0; display:flex; gap:12px;">
                <span style="color:var(--text-accent); font-weight:600; width:56px; flex-shrink:0; font-size:0.67rem; letter-spacing:1px;">URL</span>
                <span style="color:var(--text-muted);">http://fake-bank.xyz/verify</span>
              </div>
              <div style="border-bottom: 1px solid rgba(11,100,160,0.12); padding:12px 0; display:flex; gap:12px;">
                <span style="color:var(--text-accent); font-weight:600; width:56px; flex-shrink:0; font-size:0.67rem; letter-spacing:1px;">FILE</span>
                <span style="color:var(--text-muted);">invoice.exe <span style="color:#EF4444; font-size:0.72rem;">[MZ]</span></span>
              </div>
              <div style="border-bottom: 1px solid rgba(11,100,160,0.12); padding:12px 0; display:flex; gap:12px;">
                <span style="color:var(--text-accent); font-weight:600; width:56px; flex-shrink:0; font-size:0.67rem; letter-spacing:1px;">CRED</span>
                <span style="color:var(--text-muted);">password=Bank@123!</span>
              </div>
              <div style="padding:12px 0; display:flex; gap:12px;">
                <span style="color:var(--text-accent); font-weight:600; width:56px; flex-shrink:0; font-size:0.67rem; letter-spacing:1px;">ORIGIN</span>
                <span style="color:var(--text-muted);">LLM-Generated Signature</span>
              </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)

    if st.button("Execute Demo", key="btn_demo"):
        demo_email = (
            "I trust this finds you well. Your account has been flagged for "
            "suspicious activity and requires immediate verification. Please be advised "
            "that failure to comply will result in account suspension. "
            "password=Bank@123! Click the link below to secure your account immediately."
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".exe", prefix="invoice_") as tmp:
            tmp.write(b"MZ\x90\x00" + b"\x00" * 100)
            tmp_path = tmp.name

        with st.spinner("EXECUTING PIPELINE..."):
            from core.data_models import FraudSignal
            t = load_trident()
            t.reset_graph()
            result = t.detect_fraud(FraudSignal(
                email_text=demo_email,
                email_subject="URGENT: Your Account Has Been Compromised",
                sender="noreply@secure-bank.xyz",
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
    with c1: email_text = st.text_area("PAYLOAD CONTENT", height=180, key="email_body")
    with c2:
        email_subj = st.text_input("SUBJECT", key="email_subj")
        email_from = st.text_input("SENDER",  key="email_from")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Analyse Payload", key="btn_email"):
        if not email_text.strip(): st.warning("PAYLOAD CONTENT REQUIRED.")
        else:
            with st.spinner("ANALYSING..."):
                from core.data_models import FraudSignal
                t = load_trident()
                result = t.detect_fraud(FraudSignal(email_text=email_text, email_subject=email_subj or None, sender=email_from or None))
            display_result(result)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — URL CHECKER
# ─────────────────────────────────────────────────────────────────────────────
with tab_url:
    url_in = st.text_input("TARGET URL", key="url_check")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Scan URL", key="btn_url"):
        if not url_in.strip(): st.warning("TARGET URL REQUIRED.")
        else:
            with st.spinner("SCANNING..."):
                r = load_trident().url_detect.detect_malicious(url_in)
            prob, risk = r.get("malicious_probability", 0), r.get("risk", "LOW")
            color = RISK_COLORS.get(risk, "#888888")

            st.markdown(f"""
            <div class="glass-card-wrapper" style="border-left: 2px solid {color}55; margin-top:16px;">
                <div class="label-text" style="margin-bottom:10px;">URL Verification</div>
                <div style="font-family:var(--font-display); font-size:2.6rem; font-weight:500; color:{color}; margin-bottom:14px; letter-spacing:2px; text-shadow: 0 0 20px {color}44; line-height:1;">
                    {risk}
                </div>
                <div style="font-family:var(--font-mono); color:var(--text-main); margin-bottom:22px; font-weight:600; font-size:0.8rem;">
                    Probability — {prob:.0f}%
                </div>
                <div style="font-family:var(--font-mono); color:var(--text-muted); font-size:0.78rem; padding:14px 18px; background:rgba(1,8,20,0.5); border-radius:8px; border:1px solid var(--border-dim); word-break:break-all;">
                    {url_in}
                </div>
            </div>
            """, unsafe_allow_html=True)

            inds = r.get("indicators", [])
            if inds:
                ind_html = "".join(
                    f'<div style="padding:12px 0; border-bottom:1px solid rgba(11,100,160,0.1); color:var(--text-muted); font-size:0.85rem; font-family:var(--font-ui); display:flex; gap:10px; align-items:center;">'
                    f'<span style="color:var(--text-accent); font-size:0.7rem;">›</span>{i}</div>'
                    for i in inds
                )
                st.markdown(f'<div class="glass-card-wrapper" style="margin-top:18px;"><div class="label-text" style="margin-bottom:14px;">Threat Indicators</div>{ind_html}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — FULL DETECTION
# ─────────────────────────────────────────────────────────────────────────────
with tab_full:
    ca, cb = st.columns(2)
    with ca:
        full_email  = st.text_area("PAYLOAD CONTENT", height=150, key="full_email")
        full_sender = st.text_input("SENDER", key="full_sender")
    with cb:
        full_url  = st.text_input("URL", key="full_url")
        full_file = st.file_uploader("ATTACHMENT", key="full_file")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Execute Full Scan", key="btn_full"):
        if not any([full_email.strip(), full_url.strip(), full_file]): st.warning("INPUT REQUIRED.")
        else:
            att_path = None
            if full_file:
                ext = os.path.splitext(full_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(full_file.read()); att_path = tmp.name
            with st.spinner("EXECUTING..."):
                from core.data_models import FraudSignal
                t = load_trident()
                result = t.detect_fraud(FraudSignal(email_text=full_email or None, sender=full_sender or None, url=full_url or None, attachment_path=att_path))
            if att_path:
                try: os.unlink(att_path)
                except: pass
            display_result(result)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; margin-top: 100px; padding: 48px 0; border-top: 1px solid rgba(11,100,160,0.1);">
  <div style="font-family:var(--font-mono); color:var(--text-faint); font-size:0.65rem; letter-spacing:3px; font-weight:500; text-transform:uppercase;">
    Trident System Architecture &nbsp;&middot;&nbsp; V2.0.5
  </div>
</div>
""", unsafe_allow_html=True)
