import streamlit as st
import time
import os
from pathlib import Path
from agents import (
    build_reader_agent,
    build_search_agent,
    build_writer_chain,
    build_critic_chain,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · Autonomous Agent Terminal",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS, Background Video, and Cursor Glow ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,300&display=swap');

/* Reset background of standard streamlit containers to keep background video visible */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"] {
    background: transparent !important;
}

body {
    font-family: 'DM Sans', sans-serif;
    color: #eef6ff;
}

/* Background video */
#bg-video {
    position: fixed;
    right: 0;
    bottom: 0;
    min-width: 100%;
    min-height: 100%;
    width: auto;
    height: auto;
    z-index: -100;
    object-fit: cover;
    opacity: 0.35;
    pointer-events: none;
}

#bg-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at center, rgba(7, 18, 31, 0.7) 0%, rgba(3, 8, 15, 0.94) 100%);
    z-index: -99;
    pointer-events: none;
}

/* Custom scrollbars */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(10, 25, 47, 0.3);
}
::-webkit-scrollbar-thumb {
    background: rgba(0, 240, 255, 0.3);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 240, 255, 0.6);
}

/* Hide Streamlit default UI elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 3rem 2rem; max-width: 1300px; }

/* ── Hero Header ── */
.hero {
    text-align: center;
    padding: 2rem 0 1.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: #00f0ff;
    margin-bottom: 0.5rem;
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.02em;
    color: #eef6ff;
    margin: 0 0 0.5rem;
}
.hero h1 span {
    color: #00f0ff;
    text-shadow: 0 0 20px rgba(0, 240, 255, 0.3);
}
.hero-sub {
    font-size: 1.0rem;
    font-weight: 300;
    color: #a0aec0;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Divider */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 240, 255, 0.3), transparent);
    margin: 1.5rem 0;
}

/* Glassmorphism Containers */
.glass-card {
    background: rgba(10, 25, 47, 0.6) !important;
    border: 1px solid rgba(0, 240, 255, 0.15) !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    backdrop-filter: blur(16px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 0 0 10px rgba(0, 240, 255, 0.03) !important;
    margin-bottom: 1.5rem !important;
    transition: all 0.3s ease !important;
}
.glass-card:hover {
    border-color: rgba(0, 240, 255, 0.3) !important;
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.45), inset 0 0 15px rgba(0, 240, 255, 0.05) !important;
}

/* Input Fields overrides */
.stTextInput > div > div > input {
    background: rgba(10, 25, 47, 0.7) !important;
    border: 1px solid rgba(0, 240, 255, 0.2) !important;
    border-radius: 8px !important;
    color: #eef6ff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.3s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00f0ff !important;
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.3) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #00f0ff !important;
    font-weight: 700 !important;
    text-shadow: 0 0 5px rgba(0, 240, 255, 0.3);
}

/* Futuristic Neo-Cyber Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00f0ff 0%, #7000ff 100%) !important;
    color: #ffffff !important;
    border: none !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.3) !important;
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.5) !important;
    border-radius: 8px !important;
    padding: 0.75rem 2rem !important;
    width: 100%;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 0 25px rgba(0, 240, 255, 0.6), 0 0 40px rgba(112, 0, 255, 0.3) !important;
    color: #ffffff !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Agent cards formatting */
.agent-card {
    background: rgba(10, 25, 47, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 1.25rem 1.5rem !important;
    margin-bottom: 1rem !important;
    backdrop-filter: blur(8px) !important;
    transition: all 0.4s ease !important;
}
.agent-card.running {
    border-color: #00f0ff !important;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.25), inset 0 0 10px rgba(0, 240, 255, 0.05) !important;
    transform: translateX(5px) !important;
}
.agent-card.done {
    border-color: #39ff14 !important;
    box-shadow: 0 0 10px rgba(57, 255, 20, 0.15) !important;
}
.agent-card.waiting {
    opacity: 0.55 !important;
}
.agent-card-header {
    display: flex !important;
    align-items: center !important;
    gap: 0.75rem !important;
}
.agent-num {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    color: #00f0ff !important;
    opacity: 0.85 !important;
}
.agent-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: #eef6ff !important;
}
.agent-icon-wrap {
    margin-left: auto !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
}
.agent-desc {
    font-size: 0.85rem !important;
    color: #a0aec0 !important;
    margin-top: 0.4rem !important;
    line-height: 1.5 !important;
}
.neon-spinner {
    width: 12px;
    height: 12px;
    border: 2px solid rgba(0, 240, 255, 0.2);
    border-top: 2px solid #00f0ff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    display: inline-block;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.neon-checkmark {
    font-size: 1rem;
    font-weight: 900;
    color: #39ff14;
    text-shadow: 0 0 5px rgba(57, 255, 20, 0.8);
}
.neon-dot {
    font-size: 1.2rem;
    color: rgba(255, 255, 255, 0.3);
}

/* Results Formatting */
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #eef6ff;
    margin: 2rem 0 1rem;
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
}
.result-panel {
    background: rgba(10, 25, 47, 0.4);
    border: 1px solid rgba(0, 240, 255, 0.15);
    border-radius: 12px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
}
.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    color: #00f0ff;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(0, 240, 255, 0.15);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}
.result-content {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    color: #d1dbed;
    line-height: 1.6;
    white-space: pre-wrap;
}

.report-panel {
    background: rgba(10, 25, 47, 0.65) !important;
    border: 1px solid rgba(0, 240, 255, 0.25) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 240, 255, 0.1) !important;
    border-radius: 16px;
    padding: 2.5rem;
    margin-top: 1.5rem;
    backdrop-filter: blur(16px);
}
.feedback-panel {
    background: rgba(10, 25, 47, 0.65) !important;
    border: 1px solid rgba(57, 255, 20, 0.25) !important;
    box-shadow: 0 8px 32px 0 rgba(57, 255, 20, 0.1) !important;
    border-radius: 16px;
    padding: 2.5rem;
    margin-top: 1.5rem;
    backdrop-filter: blur(16px);
}

.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.panel-label.orange { color: #00f0ff; border-color: rgba(0, 240, 255, 0.2); }
.panel-label.green { color: #39ff14; border-color: rgba(57, 255, 20, 0.2); }

.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #718096;
    text-align: center;
    margin-top: 4rem;
    letter-spacing: 0.08em;
}
</style>

<!-- Absolute Background Video -->
<video autoplay loop muted playsinline id="bg-video">
  <source src="https://assets.mixkit.co/videos/preview/mixkit-futuristic-digital-particle-flow-31995-large.mp4" type="video/mp4">
</video>
<div id="bg-overlay"></div>

<!-- Cursor trail glow effect -->
<script>
try {
  const doc = window.parent !== window ? window.parent.document : document;
  
  // Custom cursor element
  let glow = doc.getElementById('cursor-glow-element');
  if (!glow) {
    glow = doc.createElement('div');
    glow.id = 'cursor-glow-element';
    Object.assign(glow.style, {
      position: 'fixed',
      width: '400px',
      height: '400px',
      background: 'radial-gradient(circle, rgba(0, 240, 255, 0.06) 0%, rgba(0, 240, 255, 0) 70%)',
      borderRadius: '50%',
      pointerEvents: 'none',
      zIndex: '999999',
      transform: 'translate(-50%, -50%)',
      left: '-1000px',
      top: '-1000px',
      mixBlendMode: 'screen',
      transition: 'opacity 0.3s ease'
    });
    doc.body.appendChild(glow);
  }

  // Handle cursor moves
  doc.addEventListener('mousemove', (e) => {
    glow.style.left = e.clientX + 'px';
    glow.style.top = e.clientY + 'px';
  });

  // Tap/Click particle bursting
  doc.addEventListener('click', (e) => {
    for (let i = 0; i < 8; i++) {
      const p = doc.createElement('div');
      Object.assign(p.style, {
        position: 'fixed',
        width: '6px',
        height: '6px',
        background: '#00f0ff',
        borderRadius: '50%',
        pointerEvents: 'none',
        zIndex: '999999',
        left: e.clientX + 'px',
        top: e.clientY + 'px',
        transform: 'translate(-50%, -50%)',
        boxShadow: '0 0 8px #00f0ff, 0 0 16px #00f0ff',
        transition: 'all 0.5s cubic-bezier(0.1, 0.8, 0.3, 1)'
      });
      doc.body.appendChild(p);
      
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 50 + 15;
      const dx = Math.cos(angle) * speed;
      const dy = Math.sin(angle) * speed;
      
      setTimeout(() => {
        p.style.left = (e.clientX + dx) + 'px';
        p.style.top = (e.clientY + dy) + 'px';
        p.style.opacity = '0';
        p.style.width = '0px';
        p.style.height = '0px';
      }, 10);
      
      setTimeout(() => p.remove(), 500);
    }
  });
} catch (err) {
  console.log("Streamlit parent frame cursor injection error handled: ", err);
}
</script>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Terminal Mode · Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <div class="hero-badge" style="
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #00f0ff;
        background: rgba(0, 240, 255, 0.08);
        border: 1px solid rgba(0, 240, 255, 0.25);
        border-radius: 999px;
        padding: 0.5rem 1.25rem;
        margin-top: 0.5rem;
        text-shadow: 0 0 5px rgba(0, 240, 255, 0.3);
    ">System Status: Active</div>
    <p class="hero-sub" style="margin-top: 1rem;">
        Collaborative AI agency designed to execute automated search engine queries, 
        content scraping, intelligence drafting, and peer critique cycles.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Layout: Input left, Monitor right ─────────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Directive",
        placeholder="e.g. Advancements in Room-Temperature Superconductors 2026",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Initialize Core Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div style="display:flex;gap:0.65rem;flex-wrap:wrap;margin-bottom:1rem;align-items:center;">
        <span style="font-family:'DM Mono',monospace;font-size:0.75rem;color:#00f0ff;letter-spacing:0.18em;text-transform:uppercase;">Directives:</span>
    """, unsafe_allow_html=True)
    examples = ["AI Agents 2026", "Nuclear Fusion breakthrough", "CRISPR Therapeutics"]
    ex_cols = st.columns(len(examples))
    for col, ex in zip(ex_cols, examples):
        if col.button(ex, key=f"example_{ex}"):
            st.session_state.topic_input = ex
    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Agent Command Center</div>', unsafe_allow_html=True)
    
    # Placeholders for 4 agents
    p1 = st.empty()
    p2 = st.empty()
    p3 = st.empty()
    p4 = st.empty()

# Helper to render the HTML representation of the status card
def agent_card_html(num: str, title: str, state: str, desc: str = "") -> str:
    status_map = {
        "waiting": ("WAITING", "rgba(255, 255, 255, 0.35)", "rgba(255, 255, 255, 0.05)"),
        "running": ("WORKING...", "#00f0ff", "rgba(0, 240, 255, 0.1)"),
        "done":    ("COMPLETED", "#39ff14", "rgba(57, 255, 20, 0.1)"),
    }
    label, color, bg = status_map.get(state, ("WAITING", "#fff", "rgba(255,255,255,0.05)"))
    
    if state == "running":
        icon = '<div class="neon-spinner"></div>'
    elif state == "done":
        icon = '<span class="neon-checkmark">✓</span>'
    else:
        icon = '<span class="neon-dot">•</span>'
        
    return f"""
    <div class="agent-card {state}">
        <div class="agent-card-header">
            <span class="agent-num">{num}</span>
            <span class="agent-title">{title}</span>
            <div class="agent-icon-wrap" style="color: {color};">
                {icon}
                <span class="agent-label" style="color: {color};">{label}</span>
            </div>
        </div>
        <div class="agent-desc">{desc}</div>
    </div>
    """

def update_pipeline_ui(active_step=None):
    results = st.session_state.results
    
    # 01 Researcher
    state1 = "waiting"
    if "search" in results:
        state1 = "done"
    elif active_step == "search":
        state1 = "running"
    p1.markdown(agent_card_html("01", "Researcher", state1, "Searching deep web index databases..."), unsafe_allow_html=True)
    
    # 02 Formatter
    state2 = "waiting"
    if "reader" in results:
        state2 = "done"
    elif active_step == "reader":
        state2 = "running"
    p2.markdown(agent_card_html("02", "Formatter", state2, "Extracting and scraping content nodes..."), unsafe_allow_html=True)
    
    # 03 Writer
    state3 = "waiting"
    if "writer" in results:
        state3 = "done"
    elif active_step == "writer":
        state3 = "running"
    p3.markdown(agent_card_html("03", "Writer", state3, "Synthesizing research into structural draft..."), unsafe_allow_html=True)
    
    # 04 Scorer
    state4 = "waiting"
    if "critic" in results:
        state4 = "done"
    elif active_step == "critic":
        state4 = "running"
    p4.markdown(agent_card_html("04", "Scorer", state4, "Reviewing findings against intelligence rules..."), unsafe_allow_html=True)

# Render initial status cards on screen draw
update_pipeline_ui()

def _parse_agent_result(result):
    if isinstance(result, dict):
        for key in ("output", "result", "text", "content"):
            value = result.get(key)
            if value is not None:
                return str(value)
        if len(result) == 1:
            return str(next(iter(result.values())))
        return str(result)
    if isinstance(result, (list, tuple)):
        return "\n".join(str(item) for item in result)
    return str(result)

# ── Run Pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please specify a core directive first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    try:
        # ── Step 1: Search ──
        update_pipeline_ui("search")
        search_agent = build_search_agent()
        sr = search_agent.invoke(
            f"Find recent, reliable and detailed information about: {topic_val}"
        )
        results["search"] = _parse_agent_result(sr)
        st.session_state.results = dict(results)
        update_pipeline_ui()

        # ── Step 2: Reader ──
        update_pipeline_ui("reader")
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke(
            f"Based on the following search results about '{topic_val}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{results['search'][:800]}"
        )
        results["reader"] = _parse_agent_result(rr)
        st.session_state.results = dict(results)
        update_pipeline_ui()

        # ── Step 3: Writer ──
        update_pipeline_ui("writer")
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = _parse_agent_result(
            build_writer_chain().invoke({
                "topic": topic_val,
                "research": research_combined,
            })
        )
        st.session_state.results = dict(results)
        update_pipeline_ui()

        # ── Step 4: Critic ──
        update_pipeline_ui("critic")
        results["critic"] = _parse_agent_result(
            build_critic_chain().invoke({"report": results["writer"]})
        )
        st.session_state.results = dict(results)
        update_pipeline_ui()

        st.session_state.running = False
        st.session_state.done = True
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline execution failed: {e}")
        st.session_state.running = False
        st.session_state.done = False

# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Intelligence Feeds</div>', unsafe_allow_html=True)

    col_raw, col_final = st.columns([4, 6])
    
    with col_raw:
        # Raw outputs in expanders
        if "search" in r:
            with st.expander("🔍 Search Signals (Raw)", expanded=False):
                st.markdown(f'<div class="result-panel"><div class="result-panel-title">Researcher Output</div>'
                            f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

        if "reader" in r:
            with st.expander("📄 Scraped Data (Raw)", expanded=False):
                st.markdown(f'<div class="result-panel"><div class="result-panel-title">Formatter Output</div>'
                            f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    with col_final:
        # Final report
        if "writer" in r:
            st.markdown("""
            <div class="report-panel">
                <div class="panel-label orange">📝 Output: Intelligence Report</div>
            """, unsafe_allow_html=True)
            st.markdown(r["writer"])   # render markdown natively
            st.markdown("</div>", unsafe_allow_html=True)

            # Download
            st.download_button(
                label="⬇  Export Dossier (.md)",
                data=r["writer"],
                file_name=f"dossier_{int(time.time())}.md",
                mime="text/markdown",
            )

        # Critic feedback
        if "critic" in r:
            st.markdown("""
            <div class="feedback-panel">
                <div class="panel-label green">🧐 Output: Quality Score & Evaluation</div>
            """, unsafe_allow_html=True)
            st.markdown(r["critic"])
            st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind Autonomous Terminal · Core v2.0 · Secured Connection
</div>
""", unsafe_allow_html=True)