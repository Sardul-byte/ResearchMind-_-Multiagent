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
    page_title="ResearchMind Terminal",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Rogue Cyberpunk UI Hijack Injections ──────────────────────────────────────
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp {background: transparent !important;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

video_html = """
<style>
#bg-video {
    position: fixed;
    right: 0;
    bottom: 0;
    min-width: 100%; 
    min-height: 100%;
    z-index: -100;
    filter: brightness(0.25); /* Darken video for text readability */
    object-fit: cover;
    pointer-events: none;
}
/* Make Streamlit's main container transparent */
.stApp {
    background-color: transparent !important;
}

@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;700&family=DM+Sans:wght@400;700&display=swap');

body {
    font-family: 'DM Sans', sans-serif;
    color: #e0e8f5;
}

/* Custom hacker command terminal styles */
.terminal-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.5rem, 5vw, 4.5rem);
    font-weight: 800;
    text-align: center;
    color: #00f0ff;
    text-shadow: 0 0 20px rgba(0, 240, 255, 0.6);
    margin-bottom: 0.5rem;
}
.terminal-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    text-align: center;
    letter-spacing: 0.4em;
    color: #ff007f;
    text-transform: uppercase;
    text-shadow: 0 0 10px rgba(255, 0, 127, 0.4);
}

.glass-card {
    background: rgba(5, 12, 24, 0.7) !important;
    border: 1px solid rgba(0, 240, 255, 0.25) !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    box-shadow: 0 0 30px rgba(0, 240, 255, 0.15), inset 0 0 15px rgba(0, 240, 255, 0.05) !important;
    margin-bottom: 2rem !important;
}

/* Custom active agent glowing panels */
.agent-card {
    background: rgba(5, 12, 24, 0.65) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 1.25rem 1.5rem !important;
    margin-bottom: 1rem !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.4s ease !important;
}
.agent-card.running {
    border-color: #00f0ff !important;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.3), inset 0 0 10px rgba(0, 240, 255, 0.1) !important;
    transform: scale(1.02) translateX(5px) !important;
}
.agent-card.done {
    border-color: #39ff14 !important;
    box-shadow: 0 0 15px rgba(57, 255, 20, 0.25) !important;
}
.agent-card.waiting {
    opacity: 0.5;
}
.agent-card-header {
    display: flex !important;
    align-items: center !important;
    gap: 0.75rem !important;
}
.agent-num {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
    color: #ff007f !important;
    font-weight: 700 !important;
}
.agent-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 700;
    color: #eef6ff !important;
}
.agent-status-tag {
    margin-left: auto !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
}
.agent-card.running .agent-status-tag {
    color: #00f0ff !important;
    animation: blink 1s infinite alternate;
}
.agent-card.done .agent-status-tag {
    color: #39ff14 !important;
    text-shadow: 0 0 8px rgba(57, 255, 20, 0.6);
}
.agent-desc {
    font-size: 0.85rem !important;
    color: #a0aec0 !important;
    margin-top: 0.4rem !important;
    line-height: 1.5 !important;
}

@keyframes blink {
    from { opacity: 0.4; }
    to { opacity: 1; }
}

/* Custom glowing outputs */
.output-card-writer {
    background: rgba(5, 12, 24, 0.75) !important;
    border: 1px solid rgba(0, 240, 255, 0.35) !important;
    border-radius: 16px !important;
    padding: 2.5rem !important;
    box-shadow: 0 0 35px rgba(0, 240, 255, 0.2) !important;
    margin-top: 2rem !important;
}
.output-card-critic {
    background: rgba(5, 12, 24, 0.75) !important;
    border: 1px solid rgba(57, 255, 20, 0.35) !important;
    border-radius: 16px !important;
    padding: 2.5rem !important;
    box-shadow: 0 0 35px rgba(57, 255, 20, 0.2) !important;
    margin-top: 2rem !important;
}
.output-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* Streamlit Input fields & buttons */
.stTextInput > div > div > input {
    background: rgba(5, 12, 24, 0.8) !important;
    border: 1px solid rgba(0, 240, 255, 0.3) !important;
    border-radius: 8px !important;
    color: #eef6ff !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.3s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00f0ff !important;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.4) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: #00f0ff !important;
}

.stButton > button {
    background: linear-gradient(135deg, #00f0ff 0%, #ff007f 100%) !important;
    color: #ffffff !important;
    border: none !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.2em !important;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.4) !important;
    border-radius: 8px !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 0 35px rgba(0, 240, 255, 0.7), 0 0 50px rgba(255, 0, 127, 0.4) !important;
}

/* Spinner anim */
.hacker-spinner {
    width: 14px;
    height: 14px;
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

.pulse-completed {
    animation: pulse 1s infinite alternate;
    font-weight: bold;
}
@keyframes pulse {
    0% { text-shadow: 0 0 5px rgba(57, 255, 20, 0.5); }
    100% { text-shadow: 0 0 15px rgba(57, 255, 20, 0.9); }
}

.notice-footer {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: rgba(255, 255, 255, 0.25);
    text-align: center;
    margin-top: 4rem;
    letter-spacing: 0.15em;
}
</style>

<video autoplay muted loop id="bg-video">
    <source src="https://cdn.pixabay.com/video/2020/05/25/40146-425316335_large.mp4" type="video/mp4">
</video>
<div id="bg-overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(3, 8, 15, 0.75); z-index: -99; pointer-events: none;"></div>

<!-- Global cursor glow & trailing script -->
<script>
try {
  const doc = window.parent !== window ? window.parent.document : document;
  const win = window.parent !== window ? window.parent : window;
  
  let glow = doc.getElementById('cyber-glow-pointer');
  if (!glow) {
    glow = doc.createElement('div');
    glow.id = 'cyber-glow-pointer';
    Object.assign(glow.style, {
      position: 'fixed',
      width: '350px',
      height: '350px',
      background: 'radial-gradient(circle, rgba(0, 240, 255, 0.15) 0%, rgba(255, 0, 127, 0.02) 50%, rgba(0,0,0,0) 70%)',
      borderRadius: '50%',
      pointerEvents: 'none',
      zIndex: '999999',
      transform: 'translate(-50%, -50%)',
      left: '-1000px',
      top: '-1000px',
      mixBlendMode: 'screen',
      transition: 'opacity 0.2s ease'
    });
    
    const core = doc.createElement('div');
    Object.assign(core.style, {
      position: 'absolute',
      left: '50%',
      top: '50%',
      width: '6px',
      height: '6px',
      background: '#00f0ff',
      borderRadius: '50%',
      transform: 'translate(-50%, -50%)',
      boxShadow: '0 0 10px #00f0ff, 0 0 20px #ff007f',
      pointerEvents: 'none'
    });
    glow.appendChild(core);
    
    doc.body.appendChild(glow);
  }

  if (win.__cyber_mousemove) {
    doc.removeEventListener('mousemove', win.__cyber_mousemove);
  }
  if (win.__cyber_click) {
    doc.removeEventListener('click', win.__cyber_click);
  }

  let lastX = 0;
  let lastY = 0;

  win.__cyber_mousemove = (e) => {
    if (glow) {
      glow.style.left = e.clientX + 'px';
      glow.style.top = e.clientY + 'px';
    }
    
    const dist = Math.hypot(e.clientX - lastX, e.clientY - lastY);
    if (dist > 20) {
      lastX = e.clientX;
      lastY = e.clientY;
      
      const p = doc.createElement('div');
      Object.assign(p.style, {
        position: 'fixed',
        width: '4px',
        height: '4px',
        background: Math.random() > 0.5 ? '#00f0ff' : '#ff007f',
        borderRadius: '50%',
        pointerEvents: 'none',
        zIndex: '999999',
        left: e.clientX + 'px',
        top: e.clientY + 'px',
        transform: 'translate(-50%, -50%)',
        boxShadow: '0 0 8px #00f0ff',
        transition: 'all 0.5s cubic-bezier(0.1, 0.8, 0.2, 1)',
        opacity: '0.85'
      });
      doc.body.appendChild(p);
      
      const dx = (Math.random() - 0.5) * 6;
      const dy = (Math.random() - 0.5) * 6;
      
      setTimeout(() => {
        p.style.transform = `translate(-50%, -50%) translate(${dx}px, ${dy}px) scale(0.1)`;
        p.style.opacity = '0';
      }, 10);
      
      setTimeout(() => p.remove(), 500);
    }
  };

  win.__cyber_click = (e) => {
    for (let i = 0; i < 6; i++) {
      const p = doc.createElement('div');
      Object.assign(p.style, {
        position: 'fixed',
        width: '5px',
        height: '5px',
        background: '#00f0ff',
        borderRadius: '50%',
        pointerEvents: 'none',
        zIndex: '999999',
        left: e.clientX + 'px',
        top: e.clientY + 'px',
        transform: 'translate(-50%, -50%)',
        boxShadow: '0 0 10px #00f0ff',
        transition: 'all 0.4s cubic-bezier(0.1, 0.8, 0.3, 1)'
      });
      doc.body.appendChild(p);
      
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 40 + 10;
      const dx = Math.cos(angle) * speed;
      const dy = Math.sin(angle) * speed;
      
      setTimeout(() => {
        p.style.left = (e.clientX + dx) + 'px';
        p.style.top = (e.clientY + dy) + 'px';
        p.style.opacity = '0';
      }, 10);
      
      setTimeout(() => p.remove(), 400);
    }
  };

  doc.addEventListener('mousemove', win.__cyber_mousemove);
  doc.addEventListener('click', win.__cyber_click);

} catch (err) {
  console.log("Cyberpunk cursor trail error handled: ", err);
}
</script>
"""
st.markdown(video_html, unsafe_allow_html=True)

# ── Title Header ──
st.markdown("""
<div style="padding-top: 1.5rem;">
    <div class="terminal-eyebrow">Terminal Mainframe // Multi-Agent Pipeline</div>
    <div class="terminal-title">Research<span>Mind</span></div>
</div>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False

# ── Layout ──
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Enter Directive",
        placeholder="e.g. LLM Reasoning Models breakthroughs 2026",
        key="topic_input",
    )
    run_btn = st.button("⚡ Initialize Mainframe Agents", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example directives
    st.markdown("""
    <div style="display:flex;gap:0.6rem;flex-wrap:wrap;margin-bottom:1rem;align-items:center;">
        <span style="font-family:'DM Mono',monospace;font-size:0.75rem;color:#00f0ff;letter-spacing:0.18em;">DIRECTIVES:</span>
    """, unsafe_allow_html=True)
    examples = ["Autonomous Agents 2026", "Quantum Encryption breakthrough", "Solid State Batteries"]
    ex_cols = st.columns(len(examples))
    for col, ex in zip(ex_cols, examples):
        if col.button(ex, key=f"ex_{ex}"):
            st.session_state.topic_input = ex
    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:1.4rem;font-weight:700;color:#00f0ff;margin:0.5rem 0 1rem;text-shadow:0 0 10px rgba(0,240,255,0.2);">Agent Monitoring Dashboard</div>', unsafe_allow_html=True)
    
    # Placeholders for 4 agents
    p1 = st.empty()
    p2 = st.empty()
    p3 = st.empty()
    p4 = st.empty()

# Helper to render the custom HTML representation of the status card
def agent_card_html(num: str, title: str, state: str, desc: str = "") -> str:
    status_map = {
        "waiting": ("WAITING", "rgba(255, 255, 255, 0.35)"),
        "running": ("WORKING...", "#00f0ff"),
        "done":    ("COMPLETED ✔", "#39ff14"),
    }
    label, color = status_map.get(state, ("WAITING", "#fff"))
    
    if state == "running":
        icon = '<div class="hacker-spinner"></div>'
        label_html = f'<span class="agent-status-tag" style="color: {color};">{icon} {label}</span>'
    elif state == "done":
        label_html = f'<span class="agent-status-tag pulse-completed" style="color: {color};">{label}</span>'
    else:
        label_html = f'<span class="agent-status-tag" style="color: {color};">{label}</span>'
        
    return f"""
    <div class="agent-card {state}">
        <div class="agent-card-header">
            <span class="agent-num">{num}</span>
            <span class="agent-title">{title}</span>
            {label_html}
        </div>
        <div class="agent-desc">{desc}</div>
    </div>
    """

def update_pipeline_ui(active_step=None):
    results = st.session_state.results
    
    # 01 Researcher (Search Agent)
    state1 = "waiting"
    if "search" in results:
        state1 = "done"
    elif active_step == "search":
        state1 = "running"
    p1.markdown(agent_card_html("01", "Researcher", state1, "Querying web databases for topic signals..."), unsafe_allow_html=True)
    
    # 02 Formatter (Reader Agent)
    state2 = "waiting"
    if "reader" in results:
        state2 = "done"
    elif active_step == "reader":
        state2 = "running"
    p2.markdown(agent_card_html("02", "Formatter", state2, "Extracting and parsing text nodes..."), unsafe_allow_html=True)
    
    # 03 Writer (Writer Chain)
    state3 = "waiting"
    if "writer" in results:
        state3 = "done"
    elif active_step == "writer":
        state3 = "running"
    p3.markdown(agent_card_html("03", "Writer", state3, "Drafting report with synthesized research..."), unsafe_allow_html=True)
    
    # 04 Scorer (Critic Chain)
    state4 = "waiting"
    if "critic" in results:
        state4 = "done"
    elif active_step == "critic":
        state4 = "running"
    p4.markdown(agent_card_html("04", "Scorer", state4, "Reviewing report and grading quality..."), unsafe_allow_html=True)

# Render initial statuses
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

# ── Core Pipeline Execution ──
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
        # ── Step 1: Researcher ──
        update_pipeline_ui("search")
        search_agent = build_search_agent()
        sr = search_agent.invoke(
            f"Find recent, reliable and detailed information about: {topic_val}"
        )
        results["search"] = _parse_agent_result(sr)
        st.session_state.results = dict(results)
        update_pipeline_ui()

        # ── Step 2: Formatter ──
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

        # ── Step 4: Scorer ──
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

# ── Output rendering ──
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:1.6rem;font-weight:800;color:#00f0ff;text-shadow:0 0 10px rgba(0,240,255,0.2);margin-bottom:1rem;">Retrieved Intelligence Dossier</div>', unsafe_allow_html=True)

    col_raw, col_final = st.columns([4, 6])
    
    with col_raw:
        if "search" in r:
            with st.expander("🔍 Search Signals (Raw)", expanded=False):
                st.markdown(f'<div style="background:rgba(5,12,24,0.5);border:1px solid rgba(0,240,255,0.15);border-radius:12px;padding:1.5rem;">'
                            f'<div style="font-family:\'DM Mono\',monospace;font-size:0.8rem;color:#00f0ff;border-bottom:1px solid rgba(0,240,255,0.15);padding-bottom:0.5rem;margin-bottom:1rem;">Researcher Output</div>'
                            f'<div style="white-space:pre-wrap;font-size:0.9rem;color:#d1dbed;line-height:1.6;">{r["search"]}</div></div>', unsafe_allow_html=True)

        if "reader" in r:
            with st.expander("📄 Scraped Data (Raw)", expanded=False):
                st.markdown(f'<div style="background:rgba(5,12,24,0.5);border:1px solid rgba(0,240,255,0.15);border-radius:12px;padding:1.5rem;">'
                            f'<div style="font-family:\'DM Mono\',monospace;font-size:0.8rem;color:#00f0ff;border-bottom:1px solid rgba(0,240,255,0.15);padding-bottom:0.5rem;margin-bottom:1rem;">Formatter Output</div>'
                            f'<div style="white-space:pre-wrap;font-size:0.9rem;color:#d1dbed;line-height:1.6;">{r["reader"]}</div></div>', unsafe_allow_html=True)

    with col_final:
        if "writer" in r:
            st.markdown("""
            <div class="output-card-writer">
                <div class="output-label orange">📝 Output: Intelligence Report</div>
            """, unsafe_allow_html=True)
            st.markdown(r["writer"])
            st.markdown("</div>", unsafe_allow_html=True)

            # Download
            st.download_button(
                label="⬇ Export Dossier (.md)",
                data=r["writer"],
                file_name=f"dossier_{int(time.time())}.md",
                mime="text/markdown",
            )

        if "critic" in r:
            st.markdown("""
            <div class="output-card-critic">
                <div class="output-label green">🧐 Output: Quality Score & Evaluation</div>
            """, unsafe_allow_html=True)
            st.markdown(r["critic"])
            st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<div class="notice-footer">
    ResearchMind Terminal v2.5 // Secured Mainframe Connection
</div>
""", unsafe_allow_html=True)