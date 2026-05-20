import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import json
import pickle
import pathlib
from pathlib import Path

st.set_page_config(page_title="WUFI Plus Analyse", layout="wide", initial_sidebar_state="expanded")

# ── Design systeem ─────────────────────────────────────────────────────────────
KLEUREN_VARIANTEN = ["#4361ee", "#f4a261", "#7b2d8b", "#00b4d8", "#e09b3d"]  # blauw, zandoranje, paars, cyaan, okergeel
KLEUR_ACCENT      = "#40916c"
KLEUR_RASTER      = "#dde8d8"
KLEUR_PAPIER      = "#f4f7f2"

CACHE_DIR = pathlib.Path(__file__).parent / "cache"

# ATG-klassen (ISSO-74 / ISO 17772-1)
ATG_KLASSEN = {
    "A": {"intercept": 20.8, "label": "ATG-A (strengste klasse)", "kleur": "#aaaaaa", "dash": "dot"},
    "B": {"intercept": 21.8, "label": "ATG-B (standaard)",        "kleur": "#888888", "dash": "dash"},
    "C": {"intercept": 22.8, "label": "ATG-C (bestaande bouw)",   "kleur": "#555555", "dash": "dashdot"},
}

def css():
    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Serif+Display&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

    <style>

    /* ── Basis ── */
    [data-testid="stAppViewBlockContainer"] { padding-top: 1.5rem !important; }
    .stApp { background: #f6f8f6; }
    html, body { font-family: 'Inter', sans-serif; color: #1c1c1e; }

    /* ── Header ── */
    .wufi-header {
        background: #ffffff;
        color: #1c1c1e;
        padding: 2rem 2.2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e4ebe5;
        border-left: 4px solid #2d6a4f;
        position: relative;
        overflow: hidden;
    }
    .wufi-header h1 {
        font-family: 'Inter', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0 0 0.35rem 0;
        letter-spacing: -0.03em;
        color: #1c1c1e !important;
    }
    .wufi-header p {
        font-size: 0.75rem;
        font-weight: 400;
        color: #636366 !important;
        margin: 0;
        letter-spacing: 0.01em;
    }
    .wufi-badge {
        display: inline-block;
        background: #e8f5ee;
        color: #2d6a4f !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.58rem;
        padding: 0.2rem 0.6rem;
        border-radius: 100px;
        margin-left: 0.7rem;
        vertical-align: middle;
        letter-spacing: 0.04em;
        border: 1px solid #b7dfca;
    }

    /* ── Zijbalk basis ── */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e4ebe5 !important;
        padding-top: 0 !important;
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1rem !important; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] small { color: #636366 !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #1c1c1e !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    [data-testid="stSidebar"] input {
        background: #ffffff !important;
        color: #1c1c1e !important;
        border-color: #e4ebe5 !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] input::placeholder {
        color: #8e8e93 !important;
    }
    [data-testid="stSidebar"] input:focus {
        border-color: #2d6a4f !important;
        color: #1c1c1e !important;
    }
    [data-testid="stSidebar"] details {
        background: #f6f8f6 !important;
        border-color: #e4ebe5 !important;
        border-radius: 12px !important;
        margin-bottom: 0.4rem !important;
    }
    [data-testid="stSidebar"] details * {
        color: #636366 !important;
        background-color: transparent !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: #f6f8f6 !important;
        border-color: #e4ebe5 !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
        color: #636366 !important;
        background-color: transparent !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
        background: #e8f5ee !important;
        color: #2d6a4f !important;
        border-color: #b7dfca !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] .stExpander {
        background: #f6f8f6 !important;
        border-color: #e4ebe5 !important;
        border-radius: 12px !important;
    }
    [data-testid="stSidebar"] .stExpander > div { background: transparent !important; }
    [data-testid="stSidebar"] summary { color: #636366 !important; }

    /* ── Zijbalk navigatie ── */
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondaryFormSubmit"],
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid #e4ebe5 !important;
        border-radius: 10px !important;
        color: #636366 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover {
        background: #e8f5ee !important;
        color: #2d6a4f !important;
        border-color: #b7dfca !important;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primaryFormSubmit"],
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
        background: #2d6a4f !important;
        border: 1px solid #2d6a4f !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(45,106,79,0.25) !important;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primaryFormSubmit"] *,
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] * {
        color: #ffffff !important;
    }

    /* ── Zijbalk sectielabel ── */
    .sidebar-label {
        font-size: 0.62rem;
        font-weight: 600;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        color: #2d6a4f !important;
        margin: 1rem 0 0.4rem 0.2rem;
    }

    /* ── Secties ── */
    .sectie-kop {
        font-family: 'Inter', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #1c1c1e !important;
        margin: 3rem 0 0.4rem 0;
        letter-spacing: -0.03em;
    }
    .sectie-lijn {
        height: 1px;
        background: linear-gradient(90deg, #c7c7cc, transparent);
        border: none;
        margin: 0 0 1.5rem 0 !important;
    }
    .sub-kop {
        font-size: 0.72rem;
        font-weight: 500;
        color: #8e8e93 !important;
        letter-spacing: 0.01em;
        margin-bottom: 1.2rem;
    }

    /* ── Indicator kaarten ── */
    .kaart {
        background: rgba(255,255,255,0.88);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1.4rem 1.5rem 1.3rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
        border: 1px solid rgba(255,255,255,0.9);
        transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
        overflow: visible;
        margin-bottom: 1rem;
    }
    .kaart:hover {
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 8px 30px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06);
    }
    .kaart-label {
        font-family: 'Inter', monospace;
        font-size: 0.62rem;
        color: #8e8e93 !important;
        text-transform: none;
        letter-spacing: 0.01em;
        margin-bottom: 0.85rem;
        font-weight: 500;
    }
    .kaart-waarden { display: flex; flex-direction: column; gap: 0.5rem; }
    .kaart-waarde { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
    .kaart-variant {
        font-size: 0.68rem;
        font-weight: 400;
        color: #636366 !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 130px;
    }
    .kaart-getal {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        font-weight: 500;
        color: #1c1c1e !important;
        white-space: nowrap;
    }
    .kaart-getal.beste  { color: #2d6a4f !important; font-weight: 700; }
    .kaart-getal.slechtste { color: #bc4749 !important; opacity: 0.82; }
    .kaart-streep {
        position: absolute; top: 0; left: 0; right: 0;
        height: 3px; border-radius: 20px 20px 0 0;
    }

    /* ── Tooltip ── */
    .kaart[data-tip]::after {
        content: attr(data-tip);
        display: none;
        position: absolute;
        bottom: calc(100% + 10px);
        left: 50%; transform: translateX(-50%);
        background: rgba(28,28,30,0.92);
        backdrop-filter: blur(16px);
        color: #f2f2f7 !important;
        font-family: 'Inter', sans-serif;
        font-size: 0.68rem;
        font-weight: 400;
        line-height: 1.55;
        padding: 0.5rem 0.9rem;
        border-radius: 12px;
        white-space: normal;
        max-width: 240px;
        width: max-content;
        z-index: 9999;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        pointer-events: none;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .kaart[data-tip]:hover::after { display: block; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(0,0,0,0.05) !important;
        border-radius: 16px !important;
        padding: 4px !important;
        gap: 2px !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        color: #636366 !important;
        border-radius: 12px !important;
        padding: 0.38rem 1rem !important;
        transition: all 0.18s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #1c1c1e !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.10), 0 1px 3px rgba(0,0,0,0.06) !important;
        font-weight: 600 !important;
    }

    /* ── Divider ── */
    hr { border-color: #c7c7cc !important; opacity: 0.4; margin: 2.5rem 0 !important; }

    /* ── Download knop ── */
    .stDownloadButton > button {
        background: rgba(44,106,79,0.08) !important;
        color: #2d6a4f !important;
        border: 1px solid rgba(44,106,79,0.2) !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 0.45rem 1.1rem !important;
        transition: all 0.18s ease !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(44,106,79,0.14) !important;
        box-shadow: 0 4px 16px rgba(44,106,79,0.18) !important;
    }

    /* ── Pill toggle voor alle horizontale radio's in de hoofdinhoud ── */
    [data-testid="stMain"] div[data-testid="stRadio"] > label {
        font-size: 0.75rem !important;
        color: #636366 !important;
        margin-bottom: 4px !important;
        font-weight: 500 !important;
    }
    [data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] {
        position: relative !important;
        background: #e8f0ea !important;
        border-radius: 20px !important;
        padding: 3px !important;
        display: inline-flex !important;
        gap: 0 !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.08) !important;
    }
    [data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] > label {
        position: relative !important;
        z-index: 1 !important;
        padding: 5px 16px !important;
        border-radius: 17px !important;
        cursor: pointer !important;
        font-size: 0.81rem !important;
        font-weight: 500 !important;
        color: #7a8f80 !important;
        white-space: nowrap !important;
        user-select: none !important;
        transition: color 0.2s ease !important;
        line-height: 1.4 !important;
    }
    [data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background: #ffffff !important;
        color: #2d6a4f !important;
        font-weight: 650 !important;
        box-shadow: 0 1px 5px rgba(0,0,0,0.14) !important;
        border-radius: 17px !important;
    }
    /* Verberg de radio-cirkel */
    [data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    </style>
    """)

css()

# ── Plotly template ────────────────────────────────────────────────────────────
wufi_template = go.layout.Template(
    layout=go.Layout(
        font=dict(family="IBM Plex Sans, sans-serif", color="#3a3028", size=12),
        title=dict(font=dict(family="Crimson Pro, serif", size=18, color="#1c2b1a")),
        paper_bgcolor=KLEUR_PAPIER,
        plot_bgcolor="#ffffff",
        xaxis=dict(gridcolor=KLEUR_RASTER, linecolor="#c8bfb4", tickfont=dict(size=11)),
        yaxis=dict(gridcolor=KLEUR_RASTER, linecolor="#c8bfb4", tickfont=dict(size=11)),
        legend=dict(
            bgcolor="rgba(250,247,242,0.9)",
            bordercolor="#d4c9b8",
            borderwidth=1,
            font=dict(size=11),
        ),
        colorway=KLEUREN_VARIANTEN,
        margin=dict(l=60, r=30, t=40, b=50),
    )
)
pio.templates["wufi"] = wufi_template

# ── Zijbalk: navigatie + projectnaam + instellingen ───────────────────────────
_DAG_NAMEN = ["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"]

# Navigatie bovenaan sidebar
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "Informatie"

def _set_pagina(naam):
    st.session_state["pagina"] = naam

_actief = st.session_state["pagina"]
_nav_c1, _nav_c2 = st.sidebar.columns(2)
with _nav_c1:
    st.button("Informatie", key="btn_informatie", on_click=_set_pagina, args=("Informatie",),
              use_container_width=True, type="primary" if _actief == "Informatie" else "secondary")
with _nav_c2:
    st.button("Analyse", key="btn_analyse", on_click=_set_pagina, args=("Analyse",),
              use_container_width=True, type="primary" if _actief == "Analyse" else "secondary")

st.sidebar.markdown('<div class="sidebar-label">Project</div>', unsafe_allow_html=True)
projectnaam = st.sidebar.text_input("Projectnaam", value="", placeholder="bijv. Kantoor Amsterdam", key="projectnaam", label_visibility="collapsed")

# Bezettingsprofielen (bronnen: DIN 18599-100 Tabel 4, NTA 8800 Bijlage B, ISO 17772-1 Bijlage B)
_BEZET_PROFIELEN = {
    "Kantoor — DIN 18599-100": {"dagen": ["Ma","Di","Wo","Do","Vr"], "van": 8,  "tot": 18},
    "Kantoor — NTA 8800":      {"dagen": ["Ma","Di","Wo","Do","Vr"], "van": 7,  "tot": 19},
    "Onderwijs — NTA 8800":    {"dagen": ["Ma","Di","Wo","Do","Vr"], "van": 8,  "tot": 17},
    "Woning — NTA 8800":       {"dagen": ["Ma","Di","Wo","Do","Vr","Za","Zo"], "van": 0, "tot": 24},
    "Aangepast":                None,
}

# Trm-profielen (bron: ISSO 74 / ISO 17772-1 Annex A)
_TRM_PROFIELEN = {
    "ISSO-74 / ISO 17772-1 (α = 0,8)": 0.80,
    "Aangepast":                        None,
}

st.sidebar.markdown('<div class="sidebar-label">Bezetting</div>', unsafe_allow_html=True)
with st.sidebar.expander("Bezettingsuren", expanded=True):
    _bezet_profiel = st.selectbox("Profiel", list(_BEZET_PROFIELEN.keys()), key="bezet_profiel", label_visibility="collapsed")
    _prof = _BEZET_PROFIELEN[_bezet_profiel]
    if _prof is not None:
        _bezet_sel  = _prof["dagen"]
        bezet_start = _prof["van"]
        bezet_eind  = _prof["tot"]
        st.caption(f"{', '.join(_bezet_sel)} · {bezet_start:02d}:00 – {bezet_eind:02d}:00")
    else:
        _bezet_sel = st.multiselect("Dagen", _DAG_NAMEN, default=["Ma","Di","Wo","Do","Vr"], key="bezet_dagen_custom")
        _b1, _b2   = st.columns(2)
        with _b1:
            bezet_start = st.number_input("Van", min_value=0, max_value=23, value=8, key="bezet_start_custom")
        with _b2:
            bezet_eind  = st.number_input("Tot", min_value=1, max_value=24, value=18, key="bezet_eind_custom")
        if bezet_eind <= bezet_start:
            st.warning("Eindtijd moet na begintijd liggen.")

st.sidebar.markdown('<div class="sidebar-label">Comfortmethode</div>', unsafe_allow_html=True)
with st.sidebar.expander("Comfortinstellingen", expanded=False):
    _trm_profiel = st.selectbox("Trm α", list(_TRM_PROFIELEN.keys()), key="trm_profiel")
    if _TRM_PROFIELEN[_trm_profiel] is not None:
        trm_alpha = _TRM_PROFIELEN[_trm_profiel]
        st.caption(f"Trm α = {trm_alpha}")
    else:
        trm_alpha = st.slider("α", min_value=0.5, max_value=0.95, value=0.8, step=0.05, key="trm_alpha_custom")
    atg_klassen_sel = st.multiselect(
        "ATG-klasse(n)",
        options=["A", "B", "C"],
        default=["B"],
        format_func=lambda k: f"Klasse {k} — {ATG_KLASSEN[k]['label'].split('(')[1].rstrip(')')}",
        key="atg_klassen",
    )
    if not atg_klassen_sel:
        atg_klassen_sel = ["B"]

bezet_dagen_nrs = [_DAG_NAMEN.index(d) for d in _bezet_sel] if _bezet_sel else list(range(5))

_pagina = st.session_state["pagina"]

# ── Header ────────────────────────────────────────────────────────────────────
_header_ondertitel = f"Hygrothermische simulatieresultaten · Comfort &amp; Energievraag · Merosch{' · ' + projectnaam if projectnaam else ''}"
st.markdown(f"""
<div class="wufi-header">
    <h1>WUFI Plus Analyse</h1>
    <p>{_header_ondertitel}</p>
</div>
""", unsafe_allow_html=True)

# ── Informatiepagina ─────────────────────────────────────────────────────────
if _pagina == "Informatie":
    st.markdown("""
    <style>
    .info-blok {
        background: rgba(255,255,255,0.88); border-radius: 16px; padding: 1.4rem 1.6rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid rgba(255,255,255,0.9);
        margin-bottom: 1rem; line-height: 1.75; font-size: 0.88rem;
    }
    .info-blok h3 { font-size: 0.95rem; font-weight: 600; margin: 0 0 0.5rem 0; color: #1c1c1e; }
    .info-blok p, .info-blok li { color: #3a3a3c; margin: 0.2rem 0; }
    .info-blok code {
        font-family: 'JetBrains Mono', monospace; background: rgba(64,145,108,0.10);
        color: #2d6a4f; padding: 0.1rem 0.35rem; border-radius: 5px; font-size: 0.82rem;
    }
    .stap-nr {
        display: inline-block; background: #2d6a4f; color: #fff; font-weight: 700;
        font-size: 0.75rem; width: 1.5rem; height: 1.5rem; border-radius: 50%;
        text-align: center; line-height: 1.5rem; margin-right: 0.5rem; vertical-align: middle;
    }
    .badge-a { display:inline-block; font-family:'JetBrains Mono',monospace; font-size:0.68rem;
               padding:0.15rem 0.5rem; border-radius:8px; background:rgba(67,97,238,0.12); color:#4361ee; }
    .badge-b { display:inline-block; font-family:'JetBrains Mono',monospace; font-size:0.68rem;
               padding:0.15rem 0.5rem; border-radius:8px; background:rgba(188,71,73,0.12); color:#bc4749; }
    </style>
    """, unsafe_allow_html=True)

    # Over de tool
    st.markdown('<div class="sectie-kop">Over de tool</div><hr class="sectie-lijn">', unsafe_allow_html=True)
    st.markdown("""<div class="info-blok">
    <p>Deze tool analyseert uurlijkse exportbestanden van <strong>WUFI Plus</strong> en berekent automatisch
    comfort- en energie-indicatoren voor maximaal <strong>vijf gevelvarianten</strong>. Varianten worden naast
    elkaar getoond voor directe vergelijking.</p>
    <p>Ontwikkeld bij Merosch. Bruikbaar voor elk WUFI Plus-project waarbij gevelvarianten worden vergeleken op
    thermisch comfort (ISSO-74 / ISO 17772-1) en energievraag.</p>
    </div>""", unsafe_allow_html=True)

    # Handleiding
    st.markdown('<div class="sectie-kop">Hoe gebruik je de tool?</div><hr class="sectie-lijn">', unsafe_allow_html=True)
    st.markdown("""<div class="info-blok">
    <p><span class="stap-nr">1</span> <strong>Voer een projectnaam in</strong> bovenaan de zijbalk (optioneel).
    De naam verschijnt in de header en in de CSV-export.</p>
    <p><span class="stap-nr">2</span> <strong>Kies een bezettingsprofiel</strong> in de zijbalk — of stel handmatig
    de dagen en uren in. Alle comfortindicatoren worden uitsluitend over de bezettingsuren berekend.</p>
    <p><span class="stap-nr">3</span> <strong>Upload bestanden</strong> per variant (maximaal 5):</p>
    <ul>
      <li><span class="badge-a">Simulatie A</span> — simulatie zonder HVAC (vrij zwevend). Basis voor comfortindicatoren.</li>
      <li><span class="badge-b">Simulatie B</span> — simulatie met verwarming en koeling actief. Basis voor energie-indicatoren.</li>
    </ul>
    <p>Per variant kun je alleen Simulatie A, alleen Simulatie B, of beide uploaden.</p>
    <p><span class="stap-nr">4</span> <strong>Lees de indicatorkaarten.</strong> Groen = beste variant, rood = slechtste voor die indicator.
    Gebruik de toggle boven de grafieken om te wisselen tussen Simulatie A en Simulatie B.</p>
    <p><span class="stap-nr">5</span> <strong>Verken de grafieken</strong> via de tabbladen onderaan de analysepagina.</p>
    <p><span class="stap-nr">6</span> <strong>Exporteer</strong> via de CSV-knop (inclusief project­metadata) of de PNG-knop onder elke grafiek.</p>
    </div>""", unsafe_allow_html=True)

    # WUFI exportformaat
    st.markdown('<div class="sectie-kop">Exportinstellingen WUFI Plus</div><hr class="sectie-lijn">', unsafe_allow_html=True)
    st.markdown("""<div class="info-blok">
    <p>Ga in WUFI Plus naar <code>Results → Export → Hourly Values → .txt</code>. Zorg dat de volgende
    uitvoergrootheden zijn aangevinkt:</p>
    <table style="width:100%;border-collapse:collapse;font-size:0.84rem;margin-top:0.5rem;">
    <tr style="border-bottom:1px solid #e5e5ea;">
      <th style="text-align:left;padding:0.4rem 0.8rem;color:#636366;">Prioriteit</th>
      <th style="text-align:left;padding:0.4rem 0.8rem;color:#636366;">Kolom in WUFI Plus</th>
      <th style="text-align:left;padding:0.4rem 0.8rem;color:#636366;">Waarvoor</th>
    </tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.4rem 0.8rem;">Verplicht</td><td style="padding:0.4rem 0.8rem;">Operative Temperature</td><td style="padding:0.4rem 0.8rem;">Alle comfortindicatoren</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.4rem 0.8rem;">Verplicht</td><td style="padding:0.4rem 0.8rem;">Temperature of Exterior Air</td><td style="padding:0.4rem 0.8rem;">Trm-berekening (ATG-grens)</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.4rem 0.8rem;">Verplicht</td><td style="padding:0.4rem 0.8rem;">Rel. Humidity of Inner Air</td><td style="padding:0.4rem 0.8rem;">RV-indicatoren</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.4rem 0.8rem;">Verplicht</td><td style="padding:0.4rem 0.8rem;">Heating Power Convective</td><td style="padding:0.4rem 0.8rem;">Warmtevraag (Simulatie B)</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.4rem 0.8rem;">Aanbevolen</td><td style="padding:0.4rem 0.8rem;">Cooling Power</td><td style="padding:0.4rem 0.8rem;">Koelvraag (Simulatie B)</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.4rem 0.8rem;">Aanbevolen</td><td style="padding:0.4rem 0.8rem;">Heat Exchange with Opaque Partitions</td><td style="padding:0.4rem 0.8rem;">Warmteflux gevel (Simulatie B)</td></tr>
    </table>
    </div>""", unsafe_allow_html=True)

    # Bezettingsprofielen
    st.markdown('<div class="sectie-kop">Bezettingsprofielen</div><hr class="sectie-lijn">', unsafe_allow_html=True)
    st.markdown("""<div class="info-blok">
    <p>De bezettingsuren bepalen over welke uren de comfortindicatoren worden berekend. Kies een standaardprofiel
    of stel handmatig in.</p>
    <table style="width:100%;border-collapse:collapse;font-size:0.84rem;margin-top:0.5rem;">
    <tr style="border-bottom:1px solid #e5e5ea;">
      <th style="text-align:left;padding:0.4rem 0.8rem;color:#636366;">Profiel</th>
      <th style="text-align:left;padding:0.4rem 0.8rem;color:#636366;">Dagen</th>
      <th style="text-align:left;padding:0.4rem 0.8rem;color:#636366;">Uren</th>
      <th style="text-align:left;padding:0.4rem 0.8rem;color:#636366;">Bron</th>
    </tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.4rem 0.8rem;">Kantoor</td><td style="padding:0.4rem 0.8rem;">Ma–Vr</td><td style="padding:0.4rem 0.8rem;">07:00–19:00</td><td style="padding:0.4rem 0.8rem;">NTA 8800 Bijlage B</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.4rem 0.8rem;">Onderwijs</td><td style="padding:0.4rem 0.8rem;">Ma–Vr</td><td style="padding:0.4rem 0.8rem;">08:00–17:00</td><td style="padding:0.4rem 0.8rem;">NTA 8800 Bijlage B</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.4rem 0.8rem;">Woning</td><td style="padding:0.4rem 0.8rem;">Ma–Zo</td><td style="padding:0.4rem 0.8rem;">00:00–24:00</td><td style="padding:0.4rem 0.8rem;">NTA 8800 Bijlage B</td></tr>
    <tr><td style="padding:0.4rem 0.8rem;">Aangepast</td><td style="padding:0.4rem 0.8rem;" colspan="3">Vrij in te stellen via de zijbalk</td></tr>
    </table>
    <p style="margin-top:0.8rem;">De <strong>Trm α</strong> (standaard 0,8 per ISSO-74 / ISO 17772-1) bepaalt hoe snel het
    lopend gemiddelde van de buitentemperatuur reageert op weersveranderingen. Een hogere α = trager, zwaardere constructie.</p>
    </div>""", unsafe_allow_html=True)

    # Comfort indicatoren
    st.markdown('<div class="sectie-kop">Comfort­indicatoren</div><hr class="sectie-lijn">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="info-blok">
        <h3>GTO — Gewogen Temperatuuroverschrijding (K²h/jr)</h3>
        <p>Kwantificeert hoeveel en hoe ernstig de operatieve temperatuur de ATG-B grens overschrijdt.
        Pieken tellen zwaarder mee door de kwadratische weging.</p>
        <p><strong>Formule:</strong> <code>Σ (T_op − ATG-B)²</code> over bezettingsuren waar T_op > ATG-B</p>
        <p><strong>Interpretatie:</strong> Lager = beter. Onder ~50 K²h/jr = nagenoeg geen oververhitting.</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="info-blok">
        <h3>ATG — Adaptieve Temperatuurgrens (ISSO-74 / ISO 17772-1)</h3>
        <p>Adaptieve comfortgrens gekoppeld aan de lopend gemiddelde buitentemperatuur (Trm).
        De formule is voor alle gebouwtypen gelijk; wat verschilt is de klasse-eis:</p>
        <table style="width:100%;border-collapse:collapse;font-size:0.82rem;margin-top:0.4rem;">
        <tr style="border-bottom:1px solid #e5e5ea;">
          <th style="text-align:left;padding:0.3rem 0.6rem;color:#636366;">Klasse</th>
          <th style="text-align:left;padding:0.3rem 0.6rem;color:#636366;">Grens</th>
          <th style="text-align:left;padding:0.3rem 0.6rem;color:#636366;">Toepassing</th>
        </tr>
        <tr style="border-bottom:1px solid #f2f2f7;">
          <td style="padding:0.3rem 0.6rem;"><strong>A</strong></td>
          <td style="padding:0.3rem 0.6rem;"><code>0,33 × Trm + 20,8°C</code></td>
          <td style="padding:0.3rem 0.6rem;">Hoge eisen: kinderdagverblijven, zorg, hoogwaardig kantoor</td>
        </tr>
        <tr style="border-bottom:1px solid #f2f2f7;">
          <td style="padding:0.3rem 0.6rem;"><strong>B</strong></td>
          <td style="padding:0.3rem 0.6rem;"><code>0,33 × Trm + 21,8°C</code></td>
          <td style="padding:0.3rem 0.6rem;">Standaard voor nieuwe kantoren en scholen</td>
        </tr>
        <tr>
          <td style="padding:0.3rem 0.6rem;"><strong>C</strong></td>
          <td style="padding:0.3rem 0.6rem;"><code>0,33 × Trm + 22,8°C</code></td>
          <td style="padding:0.3rem 0.6rem;">Bestaande bouw, renovatieprojecten</td>
        </tr>
        </table>
        <p style="margin-top:0.6rem;"><strong>Trm:</strong> exponentieel gewogen lopend gemiddelde dagtemperatuur (α = 0,8), min. 10°C</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="info-blok">
        <h3>Comfortindicatoren — Simulatie A</h3>
        <p>Comfortindicatoren worden altijd berekend op <span class="badge-a">Simulatie A</span> (vrij zwevend, geen HVAC) —
        dit toont het werkelijke thermische gedrag van de constructie zonder invloed van een installatie.</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="info-blok">
        <h3>TOjuli gem. (°C)</h3>
        <p>Gemiddelde operatieve temperatuur tijdens bezettingsuren in juli. Indicator voor zomerse piekbelasting.</p>
        <p><strong>Interpretatie:</strong> Lager = beter. Houdt geen rekening met de duur van overschrijdingen —
        gebruik in combinatie met GTO.</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="info-blok">
        <h3>T_max bezet (°C)</h3>
        <p>Hoogste operatieve temperatuur bereikt tijdens bezettingsuren over het volledige jaar. Signaleert
        extreme piekuren die in het GTO minder zichtbaar zijn.</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="info-blok">
        <h3>Relatieve luchtvochtigheid (RV)</h3>
        <p>Vier indicatoren over bezettingsuren: gemiddelde RV, percentage uren in de gezondheidszone van
        40–60%, maximum en minimum.</p>
        <p><strong>Gezondheidszone 40–60% RV:</strong> Arundel et al. (1986) — buiten dit bereik neemt de kans
        op gezondheidsklachten en schimmelgroei toe.</p>
        </div>""", unsafe_allow_html=True)

    # Energie indicatoren
    st.markdown('<div class="sectie-kop">Energie­indicatoren (Simulatie B)</div><hr class="sectie-lijn">', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("""<div class="info-blok">
        <h3>Warmtevraag &amp; Koelvraag (kWh/jr)</h3>
        <p>Totale energie die het ideale HVAC-systeem jaarlijks levert voor verwarming en koeling.
        Berekend als de som van de uurlijkse verwarmings- en koelvermogen­waarden uit WUFI Plus.</p>
        <p><strong>Let op:</strong> dit is een indicatieve vergelijkingswaarde, geen formele NTA 8800-energieprestatie.</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="info-blok">
        <h3>Piek verwarming &amp; Piek koeling (kW)</h3>
        <p>Maximaal benodigd vermogen op enig uur over het jaar. Relevant voor de dimensionering van installaties.</p>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown("""<div class="info-blok">
        <h3>Warmteflux gevel (kWh/jr)</h3>
        <p>Jaarlijkse warmtestroom door de gevelopbouw, gesplitst in twee richtingen:</p>
        <ul>
          <li><strong>Flux in:</strong> warmte die van buiten naar binnen stroomt (zomerlast)</li>
          <li><strong>Flux uit:</strong> warmte die van binnen naar buiten stroomt (winterverlies)</li>
        </ul>
        <p>Toont hoe effectief de gevel als thermische buffer functioneert.</p>
        </div>""", unsafe_allow_html=True)

    # Grafieken overzicht
    st.markdown('<div class="sectie-kop">Grafieken — overzicht</div><hr class="sectie-lijn">', unsafe_allow_html=True)
    st.markdown("""<div class="info-blok">
    <table style="width:100%;border-collapse:collapse;font-size:0.84rem;">
    <tr style="border-bottom:1px solid #e5e5ea;">
      <th style="text-align:left;padding:0.45rem 0.8rem;color:#636366;">Tabblad</th>
      <th style="text-align:left;padding:0.45rem 0.8rem;color:#636366;">Wat zie je?</th>
      <th style="text-align:left;padding:0.45rem 0.8rem;color:#636366;">Waarvoor?</th>
    </tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.45rem 0.8rem;"><strong>Adaptief comfort</strong> <span class="badge-a">A</span></td><td style="padding:0.45rem 0.8rem;">Scatter Trm vs T_operative per bezettingsuur met ATG-grenzen</td><td style="padding:0.45rem 0.8rem;">Standaardfiguur ISSO-74 / ISO 17772-1</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.45rem 0.8rem;"><strong>Overschrijding per maand</strong> <span class="badge-a">A</span></td><td style="padding:0.45rem 0.8rem;">Uren of % boven gekozen ATG-klasse per maand</td><td style="padding:0.45rem 0.8rem;">Wanneer en hoe lang treedt oververhitting op?</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.45rem 0.8rem;"><strong>Zomerperiode</strong> <span class="badge-a">A</span></td><td style="padding:0.45rem 0.8rem;">T_operative mei–september met ATG-grenslijn</td><td style="padding:0.45rem 0.8rem;">Zomerdetail, GTO inzichtelijk</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.45rem 0.8rem;"><strong>Operatieve temperatuur</strong> <span class="badge-a">A</span></td><td style="padding:0.45rem 0.8rem;">Volledig jaarverloop T_operative</td><td style="padding:0.45rem 0.8rem;">Seizoenspatroon en uitschieters</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.45rem 0.8rem;"><strong>Relatieve luchtvochtigheid</strong> <span class="badge-a">A</span></td><td style="padding:0.45rem 0.8rem;">RV binnenlucht met 40–60% gezondheidszone</td><td style="padding:0.45rem 0.8rem;">Vochthuishouding binnenklimaat</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.45rem 0.8rem;"><strong>PMV</strong> <span class="badge-a">A</span></td><td style="padding:0.45rem 0.8rem;">Jaarverloop PMV met comfortzone −0,5 tot +0,5</td><td style="padding:0.45rem 0.8rem;">Thermische behaaglijkheid (ISO 7730) · alleen als kolom aanwezig in export</td></tr>
    <tr style="border-bottom:1px solid #f2f2f7;"><td style="padding:0.45rem 0.8rem;"><strong>Warmte/Koelvraag per maand</strong> <span class="badge-b">B</span></td><td style="padding:0.45rem 0.8rem;">Maandelijks energieverbruik</td><td style="padding:0.45rem 0.8rem;">Seizoensverschillen in energievraag</td></tr>
    <tr><td style="padding:0.45rem 0.8rem;"><strong>Warmteflux gevel</strong> <span class="badge-b">B</span></td><td style="padding:0.45rem 0.8rem;">Netto warmtestroom door de gevel per maand</td><td style="padding:0.45rem 0.8rem;">Richting en omvang warmtetransport</td></tr>
    </table>
    </div>""", unsafe_allow_html=True)

    # Bronnen
    st.markdown('<div class="sectie-kop">Bronnen &amp; normen</div><hr class="sectie-lijn">', unsafe_allow_html=True)
    st.markdown("""<div class="info-blok"><ul>
    <li>ISSO-publicatie 74 — Thermische behaaglijkheid (2024)</li>
    <li>NEN-EN ISO 17772-1 — Indoor environmental input parameters for design and assessment of energy performance of buildings (2017)</li>
    <li>NTA 8800 — Energieprestatie van gebouwen (2020, incl. correctiebladen)</li>
    <li>NEN-EN-ISO 7730 — Ergonomics of the thermal environment · PMV/PPD (2005)</li>
    <li>NEN-EN 15026 — Hygrothermal performance of building components and building elements (2007)</li>
    <li>Fraunhofer IBP — WUFI Plus gebruikshandleiding</li>
    <li>Arundel et al. (1986) — Indirect health effects of relative humidity in indoor environments · <em>Environmental Health Perspectives</em></li>
    </ul></div>""", unsafe_allow_html=True)

    st.stop()

# ── Tooltips per indicator ────────────────────────────────────────────────────
TOOLTIPS = {
    "GTO (klasse A) (K²h/jr)": "Gewogen Temperatuuroverschrijding t.o.v. ATG-A · Formule: Σ(T_op − ATG-A)² over bezettingsuren. Lager = beter.",
    "GTO (klasse B) (K²h/jr)": "Gewogen Temperatuuroverschrijding t.o.v. ATG-B · Formule: Σ(T_op − ATG-B)² over bezettingsuren. Lager = beter.",
    "GTO (klasse C) (K²h/jr)": "Gewogen Temperatuuroverschrijding t.o.v. ATG-C · Formule: Σ(T_op − ATG-C)² over bezettingsuren. Lager = beter.",
    "Uren > ATG-A":           "Overschrijding ATG-klasse A (strengste klasse) · Grens: 0,33 × Trm + 20,8°C (ISSO-74 / ISO 17772-1).",
    "Uren > ATG-B":           "Overschrijding ATG-klasse B · Grens: 0,33 × Trm + 21,8°C (ISSO-74 / ISO 17772-1).",
    "Uren > ATG-C":           "Overschrijding ATG-klasse C (bestaande bouw) · Grens: 0,33 × Trm + 22,8°C (ISSO-74 / ISO 17772-1).",
    "TOjuli gem. (°C)":       "Gemiddelde operatieve temperatuur tijdens bezettingsuren in juli.",
    "T_max bezet (°C)":       "Hoogste operatieve temperatuur bereikt tijdens bezettingsuren over het hele jaar.",
    "RV gemiddeld (%)":       "Gemiddelde relatieve luchtvochtigheid tijdens bezettingsuren.",
    "% RV in 40–60%":         "Aandeel bezettingsuren met luchtvochtigheid binnen de gezondheidszone van 40–60%.",
    "RV max (%)":             "Hoogste relatieve luchtvochtigheid gemeten tijdens bezettingsuren.",
    "RV min (%)":             "Laagste relatieve luchtvochtigheid gemeten tijdens bezettingsuren.",
    "PMV gemiddeld":          "Gemiddelde Predicted Mean Vote (PMV) tijdens bezettingsuren. Schaal −3 tot +3; comfortzone −0,5 tot +0,5 (NEN-EN-ISO 7730).",
    "% PMV in [-0.5, +0.5]": "Aandeel bezettingsuren waarbij de PMV binnen de comfortzone −0,5 tot +0,5 valt (ISO 7730).",
    "Warmtevraag (kWh/jr)":   "Totale energie benodigd voor verwarming over het analysejaar.",
    "Piek verwarming (kW)":   "Maximaal benodigde verwarmingscapaciteit op enig uur.",
    "Koelvraag (kWh/jr)":     "Totale energie benodigd voor koeling over het analysejaar.",
    "Piek koeling (kW)":      "Maximaal benodigde koelcapaciteit op enig uur.",
    "Warmteflux in (kWh/jr)": "Jaarlijkse warmte die via de gevelopbouw naar binnen stroomt.",
    "Warmteflux uit (kWh/jr)":"Jaarlijkse warmte die via de gevelopbouw naar buiten stroomt.",
}

# ── Verplichte kolommen ───────────────────────────────────────────────────────
VERPLICHTE_KOLOMMEN = {"T_operative", "T_outer", "RH_inner", "Q_heating_kW"}
OPTIONELE_KOLOMMEN  = {"Q_cooling_kW", "Q_opaque_kW"}

# Trefwoorden per kolomnaam (eerste match in het bestand wint)
KOLOM_TREFWOORDEN = {
    "T_operative":      ["operative temperature"],
    "T_outer":          ["temperature of exterior air", "outer temperature"],
    "RH_outer":         ["rel. humidity of outer air", "outer rel. humidity"],
    "RH_inner":         ["rel. humidity of inner air", "inner rel. humidity"],
    "T_air":            ["temperature of interior air", "indoor air temperature", "air temperature ["],
    "T_surface_avg":    ["average surface temperature", "mean surface temperature"],
    "T_dewpoint":       ["dew point temperature of inner air", "dew point temperature ["],
    "Q_heating_kW":     ["heating power convective", "heating convective [kw]"],
    "Q_cooling_kW":     ["cooling power [kw]", "cooling [kw]"],
    "Q_opaque_kW":      ["heat exchange with opaque", "exchange with opaque partitions"],
    "Q_solar_kW":       ["solar gains [kw]"],
    "Q_ventilation_kW": ["heat flow ventilation", "ventilation [kw]"],
    "PMV":              ["predicted mean vote", "pmv [-]"],
    "PPD":              ["predicted percentage of dissatisfied", "ppd [%]"],
    "CO2":              ["co2-concentration"],
}


@st.cache_data(max_entries=12)
def parse_wufi(content: bytes):
    import re

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    lines = text.splitlines()

    # ── Stap 1: startpositie van data vinden ──
    data_start = None
    for i, line in enumerate(lines):
        if "Col. 1" in line and "Col. 2" in line:
            data_start = i + 1
            break
    if data_start is None:
        for i, line in enumerate(lines):
            if re.match(r'\s*\d{1,2}-\d{1,2}-\d{4}', line):
                data_start = i
                break
    if data_start is None:
        return None, "Koptekst niet herkend. Controleer of het bestand een WUFI Plus export is."

    # ── Stap 2: kolomnummers uit koptekst lezen (alleen vóór data_start) ──
    col_descriptions = {}  # bestandskol (1-based) → omschrijving
    for line in lines[:data_start]:
        m = re.match(r'^\s*(\d+)\s*-\s*(.+)$', line)
        if m:
            num = int(m.group(1))
            desc = m.group(2).lower().strip()
            if num >= 3:
                col_descriptions[num] = desc

    # Onze namen koppelen aan bestandskolomnummers (eerste match wint)
    col_index = {}  # onze_naam → bestandskol (1-based)
    for onze_naam, trefwoorden in KOLOM_TREFWOORDEN.items():
        for col_num in sorted(col_descriptions):
            if onze_naam in col_index:
                break
            for tw in trefwoorden:
                if tw in col_descriptions[col_num]:
                    col_index[onze_naam] = col_num
                    break

    # ── Stap 3: dataregels inlezen ──
    rows = []
    for line in lines[data_start:]:
        parts = line.split()
        if not parts or not parts[0][0].isdigit():
            continue
        try:
            # Formaat "D-M-YYYY : HH" of "DD-MM-YYYY HH"
            if len(parts) >= 3 and parts[1] == ':':
                date_raw, hour_str, data_offset = parts[0], parts[2], 3
            else:
                date_raw, hour_str, data_offset = parts[0], parts[1], 2

            # Datum padden naar DD-MM-YYYY
            d, m, y = date_raw.split('-')
            date_padded = f"{int(d):02d}-{int(m):02d}-{y}"
            hour_val = int(hour_str)

            if hour_val == 24:
                dt = pd.to_datetime(date_padded, format="%d-%m-%Y") + pd.Timedelta(days=1)
            else:
                dt = pd.to_datetime(f"{date_padded} {hour_val:02d}", format="%d-%m-%Y %H")

            vals = [float(v.replace(",", ".")) for v in parts[data_offset:]]
            rows.append([dt] + vals)
        except Exception:
            continue

    if not rows:
        return None, "Geen geldige datarijen gevonden."

    # ── Stap 4: DataFrame bouwen ──
    max_len = max(len(r) for r in rows)
    df_cols = ["datetime"] + [f"_c{i+1}" for i in range(max_len - 1)]
    for r in rows:
        while len(r) < max_len:
            r.append(0.0)
    df = pd.DataFrame(rows, columns=df_cols)

    # ── Stap 5: kolommen koppelen ──
    # Bestandskol N → df-kolom "_c{N-1}"
    # (want col 1 = datum → datetime, col 2 = tijdstap → _c1, col 3 → _c2, ...)
    if col_index:
        for onze_naam, file_col in col_index.items():
            dc = f"_c{file_col - 1}"
            if dc in df.columns:
                df[onze_naam] = df[dc]
    else:
        # Fallback: vaste volgorde (oud formaat zonder koptekstomschrijvingen)
        FALLBACK = [
            "hour", "T_outer", "RH_outer", "T_air", "T_surface_avg",
            "T_operative", "T_dewpoint", "RH_inner", "PMV", "PPD",
            "Q_heating_kW", "Q_cooling_kW",
        ]
        for i, name in enumerate(FALLBACK):
            dc = f"_c{i+1}"
            if dc in df.columns:
                df[name] = df[dc]

    # ── Stap 6: validatie ──
    ontbrekend = VERPLICHTE_KOLOMMEN - set(df.columns)
    if ontbrekend:
        return None, f"Verplichte kolommen niet gevonden: {', '.join(ontbrekend)}."

    if len(df) not in (8760, 8761, 8784, 8785):
        return None, f"Onverwacht aantal rijen: {len(df)}. Verwacht 8760 of 8784 (of +1 voor begincondities)."

    if df["datetime"].duplicated().any():
        df = df.drop_duplicates(subset="datetime").reset_index(drop=True)

    return df, None


def bereken_trm(df: pd.DataFrame, alpha: float = 0.8) -> np.ndarray:
    daily = df.set_index("datetime")["T_outer"].resample("D").mean().values
    trm = np.zeros(len(daily))
    trm[0] = daily[0]
    for i in range(1, len(daily)):
        trm[i] = (1 - alpha) * daily[i - 1] + alpha * trm[i - 1]
    trm[0] = trm[-1]
    for i in range(1, len(daily)):
        trm[i] = (1 - alpha) * daily[i - 1] + alpha * trm[i - 1]
    trm = np.maximum(trm, 10.0)
    daily_index = df.set_index("datetime")["T_outer"].resample("D").mean().index
    trm_map = pd.DataFrame({"date": daily_index, "Trm": trm})
    merged = pd.merge(
        df["datetime"].dt.normalize().rename("date").to_frame(),
        trm_map, on="date", how="left",
    )
    return merged["Trm"].values


def bereken_comfort(df_a: pd.DataFrame, bezet_start: int = 8, bezet_eind: int = 18, bezet_dagen: list | None = None, trm_alpha: float = 0.8, atg_klassen: list | None = None) -> dict:
    if bezet_dagen is None:
        bezet_dagen = list(range(5))
    if atg_klassen is None:
        atg_klassen = ["B"]
    df = df_a.copy()
    df["Trm"] = bereken_trm(df, alpha=trm_alpha)
    for k, cfg in ATG_KLASSEN.items():
        df[f"T_lim_{k}"] = 0.33 * df["Trm"] + cfg["intercept"]
    bezet = (
        df["datetime"].dt.dayofweek.isin(bezet_dagen)
        & (df["datetime"].dt.hour >= bezet_start)
        & (df["datetime"].dt.hour < bezet_eind)
    )
    df_bezet = df[bezet]
    result = {}
    for k in atg_klassen:
        t_lim = df_bezet[f"T_lim_{k}"]
        result[f"GTO (klasse {k}) (K²h/jr)"] = round(float(np.square(np.maximum(0, df_bezet["T_operative"] - t_lim)).sum()))
        result[f"Uren > ATG-{k}"]   = int((df_bezet["T_operative"] > t_lim).sum())
    juli = df_bezet[df_bezet["datetime"].dt.month == 7]
    result["TOjuli gem. (°C)"] = round(float(juli["T_operative"].mean()), 1) if len(juli) > 0 else None
    result["T_max bezet (°C)"] = round(float(df_bezet["T_operative"].max()), 1)
    rv = df.loc[bezet, "RH_inner"]
    result["RV gemiddeld (%)"] = round(float(rv.mean()), 1) if len(rv) > 0 else None
    result["% RV in 40–60%"]  = round(((rv >= 40) & (rv <= 60)).sum() / len(rv) * 100, 1) if len(rv) > 0 else None
    result["RV max (%)"]      = round(float(rv.max()), 1) if len(rv) > 0 else None
    result["RV min (%)"]      = round(float(rv.min()), 1) if len(rv) > 0 else None
    if "PMV" in df.columns:
        pmv = df.loc[bezet, "PMV"].dropna()
        if len(pmv) > 0:
            result["PMV gemiddeld"]        = round(float(pmv.mean()), 2)
            result["% PMV in [-0.5, +0.5]"] = round(((pmv >= -0.5) & (pmv <= 0.5)).sum() / len(pmv) * 100, 1)
    return result


def bereken_energie(df_b: pd.DataFrame) -> dict:
    dt = 1  # uurstap = 1h → som in kWh
    warmte = float(df_b["Q_heating_kW"].clip(lower=0).sum() * dt)
    piek_w = round(float(df_b["Q_heating_kW"].clip(lower=0).max()), 1)
    result = {
        "Warmtevraag (kWh/jr)":    round(warmte),
        "Piek verwarming (kW)":    piek_w,
    }
    if "Q_cooling_kW" in df_b.columns:
        koel   = float(df_b["Q_cooling_kW"].clip(upper=0).abs().sum() * dt)
        piek_k = round(float(df_b["Q_cooling_kW"].clip(upper=0).abs().max()), 1)
        result["Koelvraag (kWh/jr)"]   = round(koel)
        result["Piek koeling (kW)"]    = piek_k
    if "Q_opaque_kW" in df_b.columns:
        flux_in  = round(float(df_b["Q_opaque_kW"].clip(lower=0).sum() * dt))
        flux_uit = round(float(df_b["Q_opaque_kW"].clip(upper=0).abs().sum() * dt))
        result["Warmteflux in (kWh/jr)"]  = flux_in
        result["Warmteflux uit (kWh/jr)"] = flux_uit
    return result


def figuur_download(fig, bestandsnaam: str, label: str = "Download als PNG"):
    try:
        img = pio.to_image(fig, format="png", width=1400, height=540, scale=2)
        st.download_button(label=label, data=img, file_name=bestandsnaam, mime="image/png")
    except Exception:
        st.caption("PNG-export vereist kaleido. Gebruik het camera-icoon rechtsboven in de grafiek.")


# ── Sessiepersistentie: bestanden onthouden tussen herstarten ─────────────────
MAX_VARIANTEN = 5
STANDAARD_NAMEN = [f"Variant {i + 1}" for i in range(MAX_VARIANTEN)]

def _sla_cache_op(i: int):
    CACHE_DIR.mkdir(exist_ok=True)
    meta_path = CACHE_DIR / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    for sleutel in [f"naam_a_{i}", f"naam_b_{i}", f"naam_{i}"]:
        if sleutel in st.session_state:
            meta[sleutel] = st.session_state[sleutel]
    meta_path.write_text(json.dumps(meta, ensure_ascii=False))
    for ab in ("a", "b"):
        df = st.session_state.get(f"df_{ab}_{i}")
        pad = CACHE_DIR / f"df_{ab}_{i}.pkl"
        if df is not None:
            with open(pad, "wb") as f:
                pickle.dump(df, f)
        elif pad.exists():
            pad.unlink()

def _wis_cache(i: int):
    for ab in ("a", "b"):
        pad = CACHE_DIR / f"df_{ab}_{i}.pkl"
        if pad.exists():
            pad.unlink()
    meta_path = CACHE_DIR / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        for sleutel in [f"naam_a_{i}", f"naam_b_{i}", f"naam_{i}"]:
            meta.pop(sleutel, None)
        meta_path.write_text(json.dumps(meta, ensure_ascii=False))

def _laad_cache_eenmalig():
    if st.session_state.get("_cache_geladen"):
        return
    st.session_state["_cache_geladen"] = True
    if not CACHE_DIR.exists():
        return
    meta_path = CACHE_DIR / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    for i in range(MAX_VARIANTEN):
        for ab in ("a", "b"):
            pad = CACHE_DIR / f"df_{ab}_{i}.pkl"
            if pad.exists() and f"df_{ab}_{i}" not in st.session_state:
                with open(pad, "rb") as f:
                    st.session_state[f"df_{ab}_{i}"] = pickle.load(f)
        for sleutel in [f"naam_a_{i}", f"naam_b_{i}", f"naam_{i}"]:
            if sleutel in meta and sleutel not in st.session_state:
                st.session_state[sleutel] = meta[sleutel]

_laad_cache_eenmalig()

# ── Demo-data voorladen als er nog niets is geladen ───────────────────────────
_DEMO_DIR = Path(__file__).parent / "data" / "demo"
_DEMO_VARIANTEN = [
    ("HSB biobased",    "BiobasedHSB_A_SD.txt",    "BiobasedHSB_B_SD.txt"),
    ("HSB traditioneel","TraditioneelHSB_A_SD.txt","TraditioneelHSB_B_SD.txt"),
    ("KZS traditioneel","TraditioneelKZS_A_SD.txt","TraditioneelKZS_B_SD.txt"),
]

def _laad_demo_data():
    if st.session_state.get("_demo_geladen"):
        return
    if not _DEMO_DIR.exists():
        return
    # Alleen laden als er helemaal geen data is
    if any(st.session_state.get(f"df_a_{i}") is not None for i in range(MAX_VARIANTEN)):
        return
    for i, (naam, bestand_a, bestand_b) in enumerate(_DEMO_VARIANTEN):
        pad_a = _DEMO_DIR / bestand_a
        pad_b = _DEMO_DIR / bestand_b
        if pad_a.exists():
            df_a, _ = parse_wufi(pad_a.read_bytes())
            if df_a is not None:
                st.session_state[f"df_a_{i}"] = df_a
                st.session_state[f"naam_a_{i}"] = bestand_a
        if pad_b.exists():
            df_b, _ = parse_wufi(pad_b.read_bytes())
            if df_b is not None:
                st.session_state[f"df_b_{i}"] = df_b
                st.session_state[f"naam_b_{i}"] = bestand_b
        st.session_state[f"naam_{i}"] = naam
    st.session_state["_demo_geladen"] = True

_laad_demo_data()

# ── Sidebar: gevelvarianten (altijd renderen, ook op infopagina) ──────────────
st.sidebar.markdown('<div class="sidebar-label">Varianten</div>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="font-size:0.75rem;margin:0 0 0.5rem 0;opacity:0.6">Upload per variant Simulatie A en/of Simulatie B</p>', unsafe_allow_html=True)

varianten: dict[str, dict] = {}
for i in range(MAX_VARIANTEN):
    # Initialiseer naam in session state met standaardwaarde (alleen eerste keer)
    if f"naam_{i}" not in st.session_state:
        st.session_state[f"naam_{i}"] = STANDAARD_NAMEN[i]

    # Auto-naam: stel in vanuit bestandsnaam als naam nog standaard of eerder auto-gezet is
    _run_a_obj = st.session_state.get(f"run_a_{i}")
    if _run_a_obj is not None:
        _auto = _run_a_obj.name.rsplit(".", 1)[0]
        _huidige = st.session_state[f"naam_{i}"]
        _vorige_auto = st.session_state.get(f"naam_auto_{i}")
        if _huidige == STANDAARD_NAMEN[i] or _huidige == _vorige_auto:
            st.session_state[f"naam_{i}"] = _auto
            st.session_state[f"naam_auto_{i}"] = _auto

    _expander_titel = st.session_state[f"naam_{i}"]
    with st.sidebar.expander(_expander_titel, expanded=(i == 0)):
        naam = st.text_input("Naam", key=f"naam_{i}")
        run_a_file = st.file_uploader("Simulatie A — geen HVAC", type=["txt"], key=f"run_a_{i}")
        run_b_file = st.file_uploader("Simulatie B — verwarming + koeling", type=["txt"], key=f"run_b_{i}")

        # Parse en sla op in session_state zodat data bewaard blijft bij navigatie
        if run_a_file:
            df_a, fout = parse_wufi(run_a_file.read())
            if fout:
                st.error(f"Simulatie A: {fout}")
                df_a = None
            else:
                st.session_state[f"df_a_{i}"] = df_a
                st.session_state[f"naam_a_{i}"] = run_a_file.name
                _sla_cache_op(i)
        else:
            df_a = st.session_state.get(f"df_a_{i}")
            if df_a is not None:
                st.caption(f"✓ Simulatie A: {st.session_state.get(f'naam_a_{i}', 'geladen')}")

        if run_b_file:
            df_b, fout = parse_wufi(run_b_file.read())
            if fout:
                st.error(f"Simulatie B: {fout}")
                df_b = None
            else:
                st.session_state[f"df_b_{i}"] = df_b
                st.session_state[f"naam_b_{i}"] = run_b_file.name
                _sla_cache_op(i)
        else:
            df_b = st.session_state.get(f"df_b_{i}")
            if df_b is not None:
                st.caption(f"✓ Simulatie B: {st.session_state.get(f'naam_b_{i}', 'geladen')}")

        # Verwijderknop als er gecachde data is
        _heeft_cache = st.session_state.get(f"df_a_{i}") is not None or st.session_state.get(f"df_b_{i}") is not None
        if _heeft_cache and not run_a_file and not run_b_file:
            if st.button("Verwijder gegevens", key=f"del_{i}", type="secondary"):
                for _k in [f"df_a_{i}", f"df_b_{i}", f"naam_a_{i}", f"naam_b_{i}"]:
                    st.session_state.pop(_k, None)
                _wis_cache(i)
                st.rerun()

        if df_a is not None or df_b is not None:
            varianten[naam] = {"run_a": df_a, "run_b": df_b}

# ── Lege staat ────────────────────────────────────────────────────────────────
if not varianten:
    st.markdown("""
    <div style="max-width:560px; margin: 4rem auto; text-align:center;">
        <div style="font-family:'Crimson Pro',serif; font-size:3rem; color:#d4c9b8; margin-bottom:1rem;">⊞</div>
        <div style="font-family:'Crimson Pro',serif; font-size:1.4rem; color:#1c2b1a; margin-bottom:0.8rem;">
            Nog geen bestanden geladen
        </div>
        <div style="font-family:'IBM Plex Sans',sans-serif; font-size:0.85rem; color:#7a6e62; line-height:1.7;">
            Voeg gevelvarianten toe via het linkermenu.<br>
            Upload per variant een <strong>Simulatie A</strong> (vrij zwevend, geen HVAC)<br>
            en een <strong>Simulatie B</strong> (geconditioneerd, verwarming + koeling).
        </div>
        <div style="margin-top:2rem; padding:1rem; background:#f0ebe3; border-radius:4px;
                    font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:#9a8e82; text-align:left;">
            Results → Export → .txt formaat
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Data verwerken ────────────────────────────────────────────────────────────
alle_ind_comfort: dict[str, dict] = {}
alle_ind_comfort_b: dict[str, dict] = {}
alle_ind_energie: dict[str, dict] = {}
alle_run_a: dict[str, pd.DataFrame] = {}
alle_run_b: dict[str, pd.DataFrame] = {}

for naam, data in varianten.items():
    df_a, df_b = data["run_a"], data["run_b"]
    try:
        if df_a is not None:
            df_a = df_a.copy()
            df_a["Trm"] = bereken_trm(df_a, alpha=trm_alpha)
            for _k, _cfg in ATG_KLASSEN.items():
                df_a[f"T_lim_{_k}"] = 0.33 * df_a["Trm"] + _cfg["intercept"]
            alle_run_a[naam] = df_a
            alle_ind_comfort[naam] = bereken_comfort(df_a, bezet_start, bezet_eind, bezet_dagen_nrs, trm_alpha, atg_klassen_sel)
        if df_b is not None:
            df_b_c = df_b.copy()
            df_b_c["Trm"] = bereken_trm(df_b_c, alpha=trm_alpha)
            for _k, _cfg in ATG_KLASSEN.items():
                df_b_c[f"T_lim_{_k}"] = 0.33 * df_b_c["Trm"] + _cfg["intercept"]
            alle_run_b[naam] = df_b_c
            alle_ind_energie[naam] = bereken_energie(df_b)
            alle_ind_comfort_b[naam] = bereken_comfort(df_b_c, bezet_start, bezet_eind, bezet_dagen_nrs, trm_alpha, atg_klassen_sel)
    except Exception as e:
        st.error(f"Fout bij '{naam}': {e}")

# ── Waarschuwing ontbrekende optionele kolommen ───────────────────────────────
for naam, df_b in alle_run_b.items():
    ontbrekend_opt = OPTIONELE_KOLOMMEN - set(df_b.columns)
    if ontbrekend_opt:
        st.warning(
            f"**{naam} – Simulatie B:** kolom(men) niet gevonden: "
            f"{', '.join(sorted(ontbrekend_opt))}. "
            f"Controleer of deze in WUFI Plus zijn geëxporteerd. "
            f"Betreffende indicatoren worden niet getoond."
        )


# ── Kaarten renderer ──────────────────────────────────────────────────────────
ZONE_CENTRUM  = {
    "RV gemiddeld (%)": 50.0,   # beste = dichtstbij 50%
    "RV max (%)":        0.0,   # beste = laagste max (dichtstbij 0)
    "RV min (%)":      100.0,   # beste = hoogste min (dichtstbij 100)
    "PMV gemiddeld":     0.0,   # beste = dichtstbij 0 (neutraal)
}
ZONE_GRENZEN  = {
    "RV gemiddeld (%)": (40.0,  60.0),  # groen als binnen zone
    "RV max (%)":       (0.0,   60.0),  # groen als max ≤ 60%
    "RV min (%)":       (40.0, 100.0),  # groen als min ≥ 40%
    "PMV gemiddeld":    (-0.5,   0.5),  # groen als binnen comfortzone
}

def render_kaarten(indicatoren: dict[str, dict], laag_is_beter: set[str],
                   keys: list[str] | None = None, rij_grootte: int = 5,
                   geen_oordeel: set[str] | None = None):
    """Toont indicatoren als visuele kaarten per metric."""
    if not indicatoren:
        return

    geen_oordeel = geen_oordeel or set()
    namen = list(indicatoren.keys())
    alle_keys = keys if keys else list(next(iter(indicatoren.values())).keys())

    # Bepaal beste/slechtste per indicator
    def rangschik(key):
        if key in geen_oordeel:
            return {}
        vals = {n: indicatoren[n].get(key) for n in namen}
        nums = {n: v for n, v in vals.items() if isinstance(v, (int, float))}
        if len(nums) < 2:
            return {}
        if key in ZONE_CENTRUM:
            centrum = ZONE_CENTRUM[key]
            beste = min(nums, key=lambda n: abs(nums[n] - centrum))
            slechtste = max(nums, key=lambda n: abs(nums[n] - centrum))
        elif key in laag_is_beter:
            beste = min(nums, key=nums.get)
            slechtste = max(nums, key=nums.get)
        else:
            beste = max(nums, key=nums.get)
            slechtste = min(nums, key=nums.get)
        return {"beste": beste, "slechtste": slechtste}

    for rij_start in range(0, len(alle_keys), rij_grootte):
        rij_keys = alle_keys[rij_start : rij_start + rij_grootte]
        cols = st.columns(len(rij_keys), gap="medium")
        for col, key in zip(cols, rij_keys):
            rang = rangschik(key)
            with col:
                # Sorteer op werkelijke waarde: beste bovenaan, slechtste onderaan
                _vals = {n: indicatoren[n].get(key) for n in namen}
                _heeft_waarde = lambda n: _vals[n] is not None and isinstance(_vals[n], (int, float))
                if key in ZONE_CENTRUM:
                    centrum = ZONE_CENTRUM[key]
                    volgorde = sorted(namen, key=lambda n: abs(_vals[n] - centrum) if _heeft_waarde(n) else float("inf"))
                elif key in laag_is_beter:
                    volgorde = sorted(namen, key=lambda n: _vals[n] if _heeft_waarde(n) else float("inf"))
                elif key not in geen_oordeel:
                    volgorde = sorted(namen, key=lambda n: _vals[n] if _heeft_waarde(n) else float("-inf"), reverse=True)
                else:
                    volgorde = namen

                waarden_html = ""
                for naam in volgorde:
                    j = namen.index(naam)
                    val = indicatoren[naam].get(key)
                    kleur_dot = KLEUREN_VARIANTEN[j % len(KLEUREN_VARIANTEN)]
                    css_klasse = ""
                    if key in ZONE_GRENZEN and val is not None:
                        lo, hi = ZONE_GRENZEN[key]
                        css_klasse = "beste" if lo <= val <= hi else "slechtste"
                    elif rang.get("beste") == naam:
                        css_klasse = "beste"
                    elif rang.get("slechtste") == naam:
                        css_klasse = "slechtste"

                    if val is None:
                        getal_html = '<span class="kaart-getal" style="color:#c8bfb4">—</span>'
                    else:
                        if isinstance(val, int) or (isinstance(val, float) and val == int(val)):
                            val_fmt = f"{int(val):,}".replace(",", ".")
                        else:
                            val_fmt = str(val).replace(".", ",")
                        getal_html = f'<span class="kaart-getal {css_klasse}">{val_fmt}</span>'

                    kort_naam = naam.split("–")[-1].strip() if "–" in naam else naam
                    waarden_html += f"""
                    <div class="kaart-waarde">
                        <span class="kaart-variant">
                            <span style="color:{kleur_dot};margin-right:4px">●</span>{kort_naam}
                        </span>
                        {getal_html}
                    </div>"""

                tooltip = TOOLTIPS.get(key, "")
                st.markdown(f"""
                <div class="kaart" data-tip="{tooltip}">
                    <div class="kaart-label">{key}</div>
                    <div class="kaart-waarden">{waarden_html}</div>
                </div>
                """, unsafe_allow_html=True)


# ── Comfort indicatoren ───────────────────────────────────────────────────────
if alle_ind_comfort:
    st.markdown('<div class="sectie-kop">Thermisch comfort · Simulatie A — niet geconditioneerd</div><hr class="sectie-lijn">', unsafe_allow_html=True)

    _actieve_comfort = alle_ind_comfort
    _run_label = "Simulatie A — niet geconditioneerd"

    _dag_str = "–".join([_DAG_NAMEN[d].lower() for d in sorted(bezet_dagen_nrs)]) if bezet_dagen_nrs else "—"
    st.markdown(f'<div class="sub-kop">{_run_label} · ATG-methode ISSO-74 · bezettingsuren {_dag_str} {int(bezet_start):02d}:00–{int(bezet_eind):02d}:00</div>', unsafe_allow_html=True)
    _atg_keys = [f"GTO (klasse {k}) (K²h/jr)" for k in atg_klassen_sel] + [f"Uren > ATG-{k}" for k in atg_klassen_sel]
    render_kaarten(
        _actieve_comfort,
        laag_is_beter=set(_atg_keys) | {"TOjuli gem. (°C)", "T_max bezet (°C)"},
        keys=_atg_keys + ["TOjuli gem. (°C)", "T_max bezet (°C)"],
        rij_grootte=5,
    )

    st.markdown('<div class="sub-kop" style="margin-top:1.5rem">Luchtvochtigheid · gezondheidszone 40–60% RV · bezettingsuren</div>', unsafe_allow_html=True)
    render_kaarten(
        _actieve_comfort,
        laag_is_beter=set(),
        keys=["RV gemiddeld (%)", "% RV in 40–60%", "RV max (%)", "RV min (%)"],
        rij_grootte=5,
    )


# ── Energie indicatoren ───────────────────────────────────────────────────────
if alle_ind_energie:
    st.markdown('<div class="sectie-kop">Energievraag · Simulatie B — geconditioneerd</div><hr class="sectie-lijn">', unsafe_allow_html=True)
    st.markdown('<div class="sub-kop">Ideaal HVAC-systeem · netto energievraag onder geconditioneerde omstandigheden</div>', unsafe_allow_html=True)
    render_kaarten(
        alle_ind_energie,
        laag_is_beter={"Warmtevraag (kWh/jr)", "Piek verwarming (kW)", "Koelvraag (kWh/jr)", "Piek koeling (kW)"},
        geen_oordeel={"Warmteflux in (kWh/jr)", "Warmteflux uit (kWh/jr)"},
        rij_grootte=3,
    )

st.markdown("<hr>", unsafe_allow_html=True)

# ── Download-knop ─────────────────────────────────────────────────────────────
if alle_ind_comfort or alle_ind_energie:
    rijen = []
    alle_namen = list(set(list(alle_ind_comfort.keys()) + list(alle_ind_energie.keys())))
    for naam in alle_namen:
        rij = {"Variant": naam}
        rij.update(alle_ind_comfort.get(naam, {}))
        rij.update(alle_ind_energie.get(naam, {}))
        rijen.append(rij)
    df_export = pd.DataFrame(rijen)
    _dag_str_meta = "–".join([_DAG_NAMEN[d].lower() for d in sorted(bezet_dagen_nrs)]) if bezet_dagen_nrs else "—"
    _meta_regels = (
        f"# WUFI Plus Analyse — exportdatum: {pd.Timestamp.now().strftime('%d-%m-%Y %H:%M')}\n"
        + (f"# Project: {projectnaam}\n" if projectnaam else "")
        + f"# Bezettingsuren: {_dag_str_meta} {int(bezet_start):02d}:00–{int(bezet_eind):02d}:00\n"
        f"# Comfortmethode: ATG-{'/'.join(atg_klassen_sel)} (ISSO-74 adaptief) · Trm α={trm_alpha} · GTO = Σ(T_op−ATG)² (K²h/jr)\n"
        f"# Simulatie A: vrij zwevend, geen HVAC · Simulatie B: geconditioneerd (verwarming + koeling actief)\n"
        f"#\n"
    )
    _csv_data = _meta_regels + df_export.to_csv(index=False, sep=";", decimal=",")
    _, midden, _ = st.columns([2, 1, 2])
    with midden:
        st.download_button(
            label="Download resultaten (CSV)",
            data=_csv_data.encode("utf-8-sig"),
            file_name="wufi_resultaten.csv",
            mime="text/csv",
            use_container_width=True,
        )

st.markdown("<hr>", unsafe_allow_html=True)

# ── Grafieken ─────────────────────────────────────────────────────────────────
st.markdown('<div class="sectie-kop">Grafieken</div><hr class="sectie-lijn">', unsafe_allow_html=True)

# Comfortgrafieken altijd Simulatie A, energiegrafieken altijd Simulatie B
_graf_comfort_data = alle_run_a
_run_label_kort = "A"

tab_namen = []
if _graf_comfort_data:
    tab_namen += [
        "Adaptief comfort",
        "Overschrijding per maand",
        "Zomerperiode",
        "Operatieve temperatuur",
        "Relatieve luchtvochtigheid",
    ]
    if any("PMV" in df.columns for df in _graf_comfort_data.values()):
        tab_namen += ["PMV"]
if alle_run_b:
    tab_namen += [
        "Warmtevraag per maand",
        "Koelvraag per maand",
        "Warmteflux gevel",
    ]

if not tab_namen:
    st.stop()

tabs = st.tabs(tab_namen)
tab_idx = 0

if _graf_comfort_data:
    # ── Adaptief comfortdiagram ──
    with tabs[tab_idx]:
        st.caption(f"Scatter van alle bezettingsuren (Simulatie A): Trm op de X-as, operatieve temperatuur op de Y-as. Punten boven de ATG-B lijn tellen mee in de GTO. Standaardfiguur voor ISSO-74 rapportage.")
        fig = go.Figure()
        _alle_trm = pd.concat([df["Trm"] for df in _graf_comfort_data.values()])
        _trm_min = max(8.0, float(_alle_trm.min()) - 1)
        _trm_max = min(35.0, float(_alle_trm.max()) + 1)
        trm_range = np.linspace(_trm_min, _trm_max, 100)
        for k in atg_klassen_sel:
            cfg = ATG_KLASSEN[k]
            fig.add_trace(go.Scatter(
                x=trm_range, y=0.33 * trm_range + cfg["intercept"], name=cfg["label"],
                line=dict(color=cfg["kleur"], width=2.0, dash=cfg["dash"]), opacity=0.8, hoverinfo="skip",
            ))
        for i, (naam, df) in enumerate(_graf_comfort_data.items()):
            bezet_mask = (
                df["datetime"].dt.dayofweek.isin(bezet_dagen_nrs)
                & (df["datetime"].dt.hour >= int(bezet_start))
                & (df["datetime"].dt.hour < int(bezet_eind))
            )
            df_bezet = df[bezet_mask]
            fig.add_trace(go.Scatter(
                x=df_bezet["Trm"], y=df_bezet["T_operative"], name=naam,
                mode="markers",
                marker=dict(color=KLEUREN_VARIANTEN[i % len(KLEUREN_VARIANTEN)], size=3, opacity=0.25),
                hovertemplate="Trm: %{x:.1f} °C — T_op: %{y:.1f} °C<extra>" + naam + "</extra>",
            ))
        fig.update_layout(
            template="wufi",
            xaxis_title="Trm — lopend gem. buitentemperatuur (°C)",
            yaxis_title="Operatieve temperatuur (°C)",
            height=480, hovermode="closest",
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig, use_container_width=True)
        figuur_download(fig, "adaptief_comfortdiagram.png")
    tab_idx += 1

    # ── Overschrijdingsuren per maand ──
    with tabs[tab_idx]:
        _maand_namen = ["Jan", "Feb", "Mrt", "Apr", "Mei", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
        _c_overschr1, _c_overschr2 = st.columns([2, 2])
        with _c_overschr1:
            _weergave = st.radio("Weergave", ["Absolute uren", "% van bezettingsuren"], horizontal=True, key="overschr_weergave")
        with _c_overschr2:
            _atg_keuze = st.radio("ATG-klasse", atg_klassen_sel, horizontal=True, key="overschr_atg",
                                  format_func=lambda k: f"ATG-{k}")
        st.caption(f"Bezettingsuren per maand waarbij de operatieve temperatuur de ATG-{_atg_keuze} grens overschrijdt (Simulatie A).")
        fig = go.Figure()
        for i, (naam, df) in enumerate(_graf_comfort_data.items()):
            bezet_mask = (
                df["datetime"].dt.dayofweek.isin(bezet_dagen_nrs)
                & (df["datetime"].dt.hour >= int(bezet_start))
                & (df["datetime"].dt.hour < int(bezet_eind))
            )
            df_bezet = df[bezet_mask]
            overschr = df_bezet[df_bezet["T_operative"] > df_bezet[f"T_lim_{_atg_keuze}"]]
            maand_uren = overschr.groupby(overschr["datetime"].dt.month).size().reindex(range(1, 13), fill_value=0)
            if _weergave == "% van bezettingsuren":
                maand_bezet_totaal = df_bezet.groupby(df_bezet["datetime"].dt.month).size().reindex(range(1, 13), fill_value=1)
                y_vals = (maand_uren / maand_bezet_totaal * 100).round(1)
                hover = "%{y:.1f}%<extra>" + naam + "</extra>"
                y_label = f"% van bezettingsuren > ATG-{_atg_keuze}"
            else:
                y_vals = maand_uren.values
                hover = "%{y} uur<extra>" + naam + "</extra>"
                y_label = f"Uren > ATG-{_atg_keuze}"
            fig.add_trace(go.Bar(
                x=[_maand_namen[m - 1] for m in maand_uren.index],
                y=y_vals, name=naam,
                marker_color=KLEUREN_VARIANTEN[i % len(KLEUREN_VARIANTEN)],
                hovertemplate=hover,
            ))
        fig.update_layout(
            template="wufi",
            xaxis_title="Maand", yaxis_title=y_label,
            barmode="group", height=420,
            legend=dict(orientation="h", y=-0.15),
            yaxis=dict(tickformat=".1f" if _weergave == "% van bezettingsuren" else ".0f"),
        )
        st.plotly_chart(fig, use_container_width=True)
        figuur_download(fig, "overschrijding_per_maand.png")
    tab_idx += 1

    # ── Zomerdetail met ATG-B en bezettingsarcering ──
    with tabs[tab_idx]:
        st.caption(f"Gearceerde kolommen = bezettingsuren ({_dag_str} {int(bezet_start):02d}:00–{int(bezet_eind):02d}:00). GTO wordt alleen over deze uren berekend.")
        fig = go.Figure()
        first_df = next(iter(_graf_comfort_data.values()))
        zomer_all = first_df[first_df["datetime"].dt.month.isin([5, 6, 7, 8, 9])]
        for dag in zomer_all["datetime"].dt.normalize().unique():
            dag_ts = pd.Timestamp(dag)
            if dag_ts.dayofweek in bezet_dagen_nrs:
                fig.add_vrect(
                    x0=dag_ts + pd.Timedelta(hours=int(bezet_start)),
                    x1=dag_ts + pd.Timedelta(hours=int(bezet_eind)),
                    fillcolor="rgba(64,145,108,0.06)", layer="below", line_width=0,
                )
        first_zomer = first_df[first_df["datetime"].dt.month.isin([5, 6, 7, 8, 9])]
        for k in atg_klassen_sel:
            cfg = ATG_KLASSEN[k]
            fig.add_trace(go.Scatter(
                x=first_zomer["datetime"], y=first_zomer[f"T_lim_{k}"], name=cfg["label"],
                line=dict(color=cfg["kleur"], width=1.5, dash=cfg["dash"]),
                opacity=0.7,
                hovertemplate=f"%{{y:.1f}} °C<extra>{cfg['label']}</extra>",
            ))
        for i, (naam, df) in enumerate(_graf_comfort_data.items()):
            zomer = df[df["datetime"].dt.month.isin([5, 6, 7, 8, 9])]
            fig.add_trace(go.Scatter(
                x=zomer["datetime"], y=zomer["T_operative"], name=naam,
                line=dict(color=KLEUREN_VARIANTEN[i % len(KLEUREN_VARIANTEN)], width=2.0),
                opacity=0.9,
                hovertemplate="%{y:.1f} °C<extra>" + naam + "</extra>",
            ))
        fig.update_layout(
            template="wufi",
            xaxis_title="Datum", yaxis_title="Operatieve temperatuur (°C)",
            height=420, hovermode="x unified",
            legend=dict(
                orientation="v", yanchor="top", y=1, xanchor="left", x=1.08,
                bgcolor="rgba(250,247,242,0.95)", bordercolor="#d4c9b8", borderwidth=1, font=dict(size=11),
            ),
            margin=dict(l=60, r=220, t=40, b=50),
            yaxis=dict(tickformat=".1f"),
        )
        st.plotly_chart(fig, use_container_width=True)
        figuur_download(fig, "zomerperiode.png")
    tab_idx += 1

    # ── Jaargraafiek operatieve temperatuur ──
    with tabs[tab_idx]:
        st.caption(f"Operatieve temperatuur binnenruimte over het volledige jaar (Simulatie A). De operatieve temperatuur is het gemiddelde van de luchttemperatuur en de gemiddelde stralingstemperatuur, en geldt als maat voor de thermisch ervaren binnentemperatuur.")
        fig = go.Figure()
        for i, (naam, df) in enumerate(_graf_comfort_data.items()):
            fig.add_trace(go.Scatter(
                x=df["datetime"], y=df["T_operative"],
                name=naam, line=dict(color=KLEUREN_VARIANTEN[i % len(KLEUREN_VARIANTEN)], width=1.2),
                opacity=0.9,
                hovertemplate="%{y:.1f} °C<extra>" + naam + "</extra>",
            ))
        fig.update_layout(
            template="wufi",
            xaxis_title="Datum", yaxis_title="Operatieve temperatuur (°C)",
            height=420, hovermode="x unified",
            legend=dict(
                orientation="v", yanchor="middle", y=0.5,
                xanchor="left", x=1.02,
                bgcolor="rgba(250,247,242,0.95)", bordercolor="#d4c9b8", borderwidth=1,
                font=dict(size=11, color="#3a3028"),
            ),
            margin=dict(l=60, r=160, t=40, b=50),
            yaxis=dict(tickformat=".1f"),
        )
        st.plotly_chart(fig, use_container_width=True)
        figuur_download(fig, "operatieve_temperatuur_jaar.png")
    tab_idx += 1

    # ── Relatieve luchtvochtigheid ──
    with tabs[tab_idx]:
        st.caption(f"Relatieve luchtvochtigheid binnenlucht (Simulatie A). Gezondheidszone 40–60% gearceerd.")
        fig = go.Figure()
        fig.add_hrect(y0=40, y1=60, fillcolor="rgba(64,145,108,0.08)", layer="below", line_width=0,
                      annotation_text="40–60% zone", annotation_position="right",
                      annotation_font=dict(color=KLEUR_ACCENT, size=11))
        for i, (naam, df) in enumerate(_graf_comfort_data.items()):
            fig.add_trace(go.Scatter(
                x=df["datetime"], y=df["RH_inner"], name=naam,
                line=dict(color=KLEUREN_VARIANTEN[i % len(KLEUREN_VARIANTEN)], width=2.0),
                opacity=0.9,
                hovertemplate="%{y:.1f} %<extra>" + naam + "</extra>",
            ))
        fig.update_layout(
            template="wufi",
            xaxis_title="Datum", yaxis_title="Relatieve luchtvochtigheid (%)",
            height=420, hovermode="x unified",
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02,
                        bgcolor="rgba(250,247,242,0.95)", bordercolor="#d4c9b8", borderwidth=1, font=dict(size=11)),
            margin=dict(l=60, r=160, t=40, b=50),
            yaxis=dict(tickformat=".1f", range=[0, 100]),
        )
        st.plotly_chart(fig, use_container_width=True)
        figuur_download(fig, "relatieve_luchtvochtigheid.png")
    tab_idx += 1

    _heeft_pmv_graf = any("PMV" in df.columns for df in _graf_comfort_data.values())
    if _heeft_pmv_graf:
        with tabs[tab_idx]:
            st.caption("Predicted Mean Vote (PMV) over het volledige jaar (Simulatie A · bezettingsuren gemarkeerd). Comfortzone −0,5 tot +0,5 gearceerd (ISO 7730).")
            fig = go.Figure()
            fig.add_hrect(
                y0=-0.5, y1=0.5,
                fillcolor="rgba(64,145,108,0.10)", layer="below", line_width=0,
                annotation_text="Comfortzone", annotation_position="right",
                annotation_font=dict(color="#2c6a4f", size=11),
            )
            fig.add_hline(y=0, line=dict(color="#2c6a4f", width=1.5, dash="dot"), opacity=0.5)
            for i, (naam, df) in enumerate(_graf_comfort_data.items()):
                if "PMV" not in df.columns:
                    continue
                fig.add_trace(go.Scatter(
                    x=df["datetime"], y=df["PMV"],
                    name=naam,
                    line=dict(color=KLEUREN_VARIANTEN[i % len(KLEUREN_VARIANTEN)], width=2.0),
                    opacity=0.85,
                    hovertemplate="%{y:.2f}<extra>" + naam + "</extra>",
                ))
            fig.update_layout(
                template="wufi",
                xaxis_title="Datum", yaxis_title="PMV (−)",
                height=420, hovermode="x unified",
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02,
                            bgcolor="rgba(250,247,242,0.95)", bordercolor="#d4c9b8", borderwidth=1, font=dict(size=11)),
                margin=dict(l=60, r=160, t=40, b=50),
                yaxis=dict(tickformat=".2f", range=[-3, 3]),
            )
            st.plotly_chart(fig, use_container_width=True)
            figuur_download(fig, "pmv_jaarverloop.png")
        tab_idx += 1


if alle_run_b:
    maand_namen = ["Jan", "Feb", "Mrt", "Apr", "Mei", "Jun",
                   "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]

    with tabs[tab_idx]:
        st.caption("Maandelijkse warmtevraag per variant (Simulatie B — geconditioneerd). Vergelijking toont indicatieve relatieve verschillen tussen de constructies.")
        fig = go.Figure()
        for i, (naam, df) in enumerate(alle_run_b.items()):
            maandelijks = (
                df.assign(maand=df["datetime"].dt.month)
                .groupby("maand")["Q_heating_kW"].sum().clip(lower=0)
            )
            fig.add_trace(go.Bar(
                x=[maand_namen[m - 1] for m in maandelijks.index],
                y=maandelijks.values, name=naam,
                marker_color=KLEUREN_VARIANTEN[i % len(KLEUREN_VARIANTEN)],
                hovertemplate="%{y:.0f} kWh<extra>" + naam + "</extra>",
            ))
        fig.update_layout(
            template="wufi",
            xaxis_title="Maand", yaxis_title="Warmtevraag (kWh)",
            barmode="group", height=420,
            legend=dict(orientation="h", y=-0.15),
            yaxis=dict(tickformat=".0f"),
        )
        st.plotly_chart(fig, use_container_width=True)
        figuur_download(fig, "warmtevraag_per_maand.png")
    tab_idx += 1

    with tabs[tab_idx]:
        heeft_koel = any("Q_cooling_kW" in df.columns for df in alle_run_b.values())
        if not heeft_koel:
            st.info("Kolom Q_cooling_kW niet gevonden. Controleer of deze in WUFI Plus is geëxporteerd.")
        else:
            st.caption("Maandelijkse koelvraag per variant (Simulatie B — geconditioneerd). Vergelijking toont indicatieve relatieve verschillen tussen de constructies.")
            fig = go.Figure()
            for i, (naam, df) in enumerate(alle_run_b.items()):
                if "Q_cooling_kW" not in df.columns:
                    continue
                maandelijks = (
                    df.assign(maand=df["datetime"].dt.month)
                    .groupby("maand")["Q_cooling_kW"]
                    .apply(lambda x: x.clip(upper=0).abs().sum())
                )
                fig.add_trace(go.Bar(
                    x=[maand_namen[m - 1] for m in maandelijks.index],
                    y=maandelijks.values, name=naam,
                    marker_color=KLEUREN_VARIANTEN[i % len(KLEUREN_VARIANTEN)],
                    hovertemplate="%{y:.0f} kWh<extra>" + naam + "</extra>",
                ))
            fig.update_layout(
                template="wufi",
                xaxis_title="Maand", yaxis_title="Koelvraag (kWh)",
                barmode="group", height=420,
                legend=dict(orientation="h", y=-0.15),
                yaxis=dict(tickformat=".0f"),
            )
            st.plotly_chart(fig, use_container_width=True)
            figuur_download(fig, "koelvraag_per_maand.png")
    tab_idx += 1

    with tabs[tab_idx]:
        heeft_flux = any("Q_opaque_kW" in df.columns for df in alle_run_b.values())
        if not heeft_flux:
            st.info("Kolom Q_opaque_kW niet gevonden in de exportbestanden. Controleer of deze kolom in WUFI Plus is geëxporteerd.")
        else:
            st.caption("Netto warmteflux door de gevelopbouw per maand (Simulatie B). Positief = warmte naar binnen, negatief = warmte naar buiten.")
            fig = go.Figure()
            for i, (naam, df) in enumerate(alle_run_b.items()):
                if "Q_opaque_kW" not in df.columns:
                    continue
                maandelijks = (
                    df.assign(maand=df["datetime"].dt.month)
                    .groupby("maand")["Q_opaque_kW"].sum()
                )
                fig.add_trace(go.Bar(
                    x=[maand_namen[m - 1] for m in maandelijks.index],
                    y=maandelijks.values, name=naam,
                    marker_color=KLEUREN_VARIANTEN[i % len(KLEUREN_VARIANTEN)],
                    hovertemplate="%{y:.0f} kWh<extra>" + naam + "</extra>",
                ))
            fig.add_hline(y=0, line_color="#3a3028", line_width=1)
            fig.update_layout(
                template="wufi",
                xaxis_title="Maand", yaxis_title="Warmteflux gevel (kWh)",
                barmode="group", height=420,
                legend=dict(orientation="h", y=-0.15),
                yaxis=dict(tickformat=".0f"),
            )
            st.plotly_chart(fig, use_container_width=True)
            figuur_download(fig, "warmteflux_gevel.png")
