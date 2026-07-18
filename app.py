import streamlit as st
from datetime import datetime

from agent import get_search_agent, get_reader_agent, writer_chain, critic_chain


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def to_text(obj) -> str:
    """Normalize LangChain outputs (AIMessage / str / dict) into plain text."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if hasattr(obj, "content"):
        return obj.content
    if isinstance(obj, dict) and "content" in obj:
        return obj["content"]
    return str(obj)


def card(content_md: str, extra_class: str = ""):
    st.markdown(
        f"<div class='report-card fade-up {extra_class}'>\n\n{content_md}\n\n</div>",
        unsafe_allow_html=True,
    )


def run_pipeline(topic: str, status_box):
    state = {}

    status_box.update(label="🔎  Casting a wide net across the web...", state="running")
    search_agent = get_search_agent()
    search_results = search_agent.invoke(
        {"messages": f"Find recent, reliable and detailed information about: {topic}"}
    )
    state["search_results"] = to_text(search_results["messages"][-1].content)

    status_box.update(label="📖  Reading the most promising source...", state="running")
    reader_agent = get_reader_agent()
    reader_results = reader_agent.invoke(
        {
            "messages": f"""Based on the following search results about '{topic}',
        pick the most relevant URL and scrape it for deeper content.\n\n
        Search Results: \n{state['search_results'][:800]}"""
        }
    )
    state["scraped_content"] = to_text(reader_results["messages"][-1].content)

    status_box.update(label="✍️  Drafting the report...", state="running")
    combined_research = (
        f"SEARCH RESULTS:\n {state['search_results']}",
        f"SCRAPED CONTENT:\n {state['scraped_content']}",
    )
    report = writer_chain.invoke(
        {"topic": topic, "research": combined_research, "report": None, "feedback": None}
    )
    state["report"] = to_text(report)

    status_box.update(label="🧠  Critiquing the draft...", state="running")
    improvements = critic_chain.invoke({"report": state["report"]})
    state["improvements"] = to_text(improvements)

    status_box.update(label="✨  Polishing the final report...", state="running")
    final_report = writer_chain.invoke(
        {"topic": None, "research": None, "report": state["report"], "feedback": state["improvements"]}
    )
    state["final_report"] = to_text(final_report)

    status_box.update(label="✓ Research complete", state="complete")
    return state


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Nova — Deep Research", page_icon="✦", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None
if "topic" not in st.session_state:
    st.session_state.topic = None

# ---------------------------------------------------------------------------
# CSS — vibrant light theme, blobs, marquee, cards
# ---------------------------------------------------------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

html { scroll-behavior: smooth; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3, .brand, .hero-title { font-family: 'Space Grotesk', sans-serif; }

#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stToolbar"] { visibility: hidden; height: 0; }
[data-testid="stSidebar"] { display: none; }
[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
}
.block-container { padding-top: 1rem !important; max-width: 1150px; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #FFF9F2 0%, #FFF3E9 40%, #FFFFFF 100%);
}

/* ---------- floating vibrant blobs ---------- */
.blob-field { position: relative; height: 0; }
.blob {
    position: absolute;
    border-radius: 58% 42% 65% 35% / 45% 55% 45% 55%;
    filter: blur(30px);
    opacity: 0.55;
    z-index: 0;
    animation: float 14s ease-in-out infinite;
}
.blob-a { width: 340px; height: 340px; top: -180px; left: -80px;
    background: radial-gradient(circle at 30% 30%, #FF5FA2, #FF3D81); animation-delay: 0s; }
.blob-b { width: 280px; height: 280px; top: -120px; right: -60px;
    background: radial-gradient(circle at 60% 40%, #7C5CFF, #4F2AD1); animation-delay: -4s; }
.blob-c { width: 220px; height: 220px; top: 60px; left: 45%;
    background: radial-gradient(circle at 40% 40%, #FFC93C, #FF9F1C); animation-delay: -8s; opacity: 0.45;}
.blob-d { width: 200px; height: 200px; top: -40px; right: 30%;
    background: radial-gradient(circle at 50% 50%, #00D6C6, #00A8AE); animation-delay: -2s; opacity: 0.4;}
@keyframes float {
    0%   { transform: translate(0,0) rotate(0deg) scale(1); }
    33%  { transform: translate(18px,-22px) rotate(10deg) scale(1.06); }
    66%  { transform: translate(-16px,14px) rotate(-8deg) scale(0.97); }
    100% { transform: translate(0,0) rotate(0deg) scale(1); }
}

/* ---------- header ---------- */
.topnav {
    position: sticky; top: 0; z-index: 50;
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 6px; margin-bottom: 10px;
    backdrop-filter: blur(10px);
    background: rgba(255,249,242,0.75);
    border-bottom: 1px solid rgba(0,0,0,0.06);
}
.brand { font-weight: 800; font-size: 1.35rem; color: #1a1a2e; display:flex; align-items:center; gap:8px;}
.brand span.dot { color: #FF3D81; }
.nav-links a {
    color: #4a4a5a; text-decoration: none; font-weight: 500; margin-left: 26px; font-size: 0.95rem;
    transition: color 0.15s ease;
}
.nav-links a:hover { color: #FF3D81; }

/* ---------- hero ---------- */
.hero { position: relative; z-index: 1; text-align: center; padding: 64px 10px 20px; }
.pill-tag {
    display: inline-block; padding: 6px 16px; border-radius: 999px;
    background: linear-gradient(90deg, #FFE3EF, #EFE6FF);
    color: #7C2AA0; font-weight: 600; font-size: 0.82rem; letter-spacing: 0.3px;
    margin-bottom: 22px; border: 1px solid rgba(124,42,160,0.15);
}
.hero-title {
    font-size: 3.4rem; font-weight: 800; line-height: 1.08; color: #16161f;
    margin-bottom: 14px;
}
.hero-title .grad {
    background: linear-gradient(90deg, #FF3D81, #7C5CFF 55%, #00C2CB);
    background-size: 200% auto;
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    animation: shine 6s linear infinite;
}
@keyframes shine { to { background-position: 200% center; } }
.hero-sub { font-size: 1.12rem; color: #5c5c6e; max-width: 620px; margin: 0 auto 36px; line-height: 1.6; }

/* ---------- marquee ---------- */
.marquee-wrap { overflow: hidden; position: relative; z-index: 1; padding: 14px 0 30px;
    -webkit-mask-image: linear-gradient(90deg, transparent, #000 10%, #000 90%, transparent);
    mask-image: linear-gradient(90deg, transparent, #000 10%, #000 90%, transparent); }
.marquee { display: flex; width: max-content; gap: 14px; animation: scroll 20s linear infinite; }
.marquee span {
    white-space: nowrap; padding: 9px 20px; border-radius: 999px; font-weight: 600; font-size: 0.9rem;
    background: white; border: 1px solid rgba(0,0,0,0.08); color: #3a3a4a;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
}
@keyframes scroll { from { transform: translateX(0); } to { transform: translateX(-50%); } }

/* ---------- search bar ---------- */
.search-zone { position: relative; z-index: 2; max-width: 720px; margin: 0 auto; }
div[data-testid="stTextInput"] input {
    background: white !important; border: 2px solid #efe6ff !important; border-radius: 999px !important;
    padding: 14px 22px !important; font-size: 1.05rem !important; color: #16161f !important;
    box-shadow: 0 10px 30px rgba(124,92,255,0.12);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #FF3D81 !important; box-shadow: 0 10px 34px rgba(255,61,129,0.22) !important;
}
div[data-testid="stTextInput"] label { display: none; }
.stButton > button {
    background: linear-gradient(135deg, #FF3D81, #7C5CFF);
    color: white; border: none; border-radius: 999px; padding: 0.75rem 1rem;
    font-weight: 700; font-size: 1.02rem; width: 100%;
    box-shadow: 0 10px 26px rgba(255,61,129,0.35);
    transition: transform 0.16s ease, box-shadow 0.16s ease;
}
.stButton > button:hover { transform: translateY(-2px) scale(1.015); box-shadow: 0 14px 32px rgba(124,92,255,0.4); }
.stButton > button:active { transform: translateY(0) scale(0.98); }

.chip-row { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-top: 16px; }
.chip-row button {
    background: white !important; color: #4a4a5a !important; border: 1px solid rgba(0,0,0,0.08) !important;
    box-shadow: none !important; font-weight: 500 !important; font-size: 0.85rem !important;
    padding: 6px 14px !important; border-radius: 999px !important; width: auto !important;
}
.chip-row button:hover { border-color: #FF3D81 !important; color: #FF3D81 !important; transform: none !important; }

/* ---------- how it works ---------- */
.section-title { text-align: center; font-size: 1.9rem; font-weight: 800; color: #16161f; margin: 70px 0 6px; }
.section-sub { text-align: center; color: #6a6a7a; margin-bottom: 36px; }
.step-card {
    background: white; border-radius: 20px; padding: 26px 20px; text-align: left;
    border: 1px solid rgba(0,0,0,0.06); box-shadow: 0 8px 24px rgba(0,0,0,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease; height: 100%;
}
.step-card:hover { transform: translateY(-6px); box-shadow: 0 16px 32px rgba(124,92,255,0.16); }
.step-icon {
    width: 46px; height: 46px; border-radius: 14px; display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; margin-bottom: 14px;
}
.step-card h4 { margin: 0 0 6px; font-size: 1.05rem; color: #16161f; }
.step-card p { margin: 0; color: #6a6a7a; font-size: 0.9rem; line-height: 1.5; }

/* ---------- report cards ---------- */
.report-card {
    background: white; border-radius: 20px; padding: 1.8rem 2rem; margin-top: 6px;
    border: 1px solid rgba(0,0,0,0.06); box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    color: #26263a; line-height: 1.7;
}
.report-card h1, .report-card h2, .report-card h3 { color: #16161f; }
.report-card a { color: #7C5CFF; }
.fade-up { animation: fadeUp 0.6s ease both; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }

[data-testid="stTabs"] button { color: #7a7a8a; font-weight: 600; border-radius: 999px !important; }
[data-testid="stTabs"] button[aria-selected="true"] {
    color: white !important; background: linear-gradient(135deg, #FF3D81, #7C5CFF) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 8px; background: #FFF3E9; padding: 6px; border-radius: 999px; }
[data-testid="stExpander"] {
    background: white; border: 1px solid rgba(0,0,0,0.06); border-radius: 16px; box-shadow: 0 6px 18px rgba(0,0,0,0.03);
}
[data-testid="stStatus"] { background: white; border: 1px solid rgba(0,0,0,0.06); border-radius: 16px; }

/* ---------- footer ---------- */
.footer {
    margin-top: 90px; padding: 34px 10px 20px; text-align: center; color: #8a8a9a; font-size: 0.88rem;
    border-top: 1px solid rgba(0,0,0,0.06);
}
.footer .brand { justify-content: center; font-size: 1.1rem; margin-bottom: 6px;}
.footer-links { margin-top: 10px; }
.footer-links a { color: #6a6a7a; text-decoration: none; margin: 0 10px; font-weight: 500; }
.footer-links a:hover { color: #FF3D81; }

::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-thumb { background: #ffd0e2; border-radius: 8px; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
<div class="topnav">
    <div class="brand">✦ Nova<span class="dot">.</span></div>
    <div class="nav-links">
        <a href="#how-it-works">How it works</a>
        <a href="#try-it">Try it</a>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Hero + blobs
# ---------------------------------------------------------------------------

st.markdown(
    """
<div class="blob-field">
    <div class="blob blob-a"></div>
    <div class="blob blob-b"></div>
    <div class="blob blob-c"></div>
    <div class="blob blob-d"></div>
</div>
<div class="hero">
    <div class="pill-tag">✦ Multi-agent research, in one click</div>
    <div class="hero-title">Ask anything.<br>Get a <span class="grad">real report</span> back.</div>
    <div class="hero-sub">Nova sends out agents to search the web, read the best source in depth,
    draft a report, tear it apart, then rewrite it better — so you get a finished answer, not a link dump.</div>
</div>
<div class="marquee-wrap">
    <div class="marquee">
        <span>🔎 Live web search</span><span>📖 Deep reading</span><span>✍️ Auto-drafting</span>
        <span>🧠 Self-critique</span><span>✨ Polished output</span><span>⚡ Minutes, not hours</span>
        <span>🔎 Live web search</span><span>📖 Deep reading</span><span>✍️ Auto-drafting</span>
        <span>🧠 Self-critique</span><span>✨ Polished output</span><span>⚡ Minutes, not hours</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Search zone
# ---------------------------------------------------------------------------

st.markdown('<div id="try-it"></div>', unsafe_allow_html=True)
st.markdown('<div class="search-zone">', unsafe_allow_html=True)

col1, col2 = st.columns([5, 1.3], vertical_alignment="center")
with col1:
    topic_input = st.text_input(
        "topic", placeholder="e.g. Impact of quantum computing on cryptography...", label_visibility="collapsed"
    )
with col2:
    run_clicked = st.button("✦ Research", type="primary", use_container_width=True)

if st.session_state.history:
    st.markdown('<div class="chip-row">', unsafe_allow_html=True)
    chip_cols = st.columns(len(st.session_state.history[-5:]))
    for i, item in enumerate(reversed(st.session_state.history[-5:])):
        with chip_cols[i]:
            if st.button(f"🗂 {item['topic'][:22]}", key=f"chip_{i}"):
                st.session_state.result = item["state"]
                st.session_state.topic = item["topic"]
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# How it works
# ---------------------------------------------------------------------------

st.markdown('<div id="how-it-works"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">How Nova thinks</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Five agent steps, fully automated.</div>', unsafe_allow_html=True)

steps = [
    ("🔎", "#FFE3EF", "Search", "Scans the live web for recent, reliable sources on your topic."),
    ("📖", "#EFE6FF", "Read", "Picks the strongest result and scrapes it for real depth."),
    ("✍️", "#FFF3D6", "Draft", "Writes a first version of the report from everything gathered."),
    ("🧠", "#DFFAF3", "Critique", "Reviews its own draft and lists concrete improvements."),
    ("✨", "#FFE3EF", "Finalize", "Rewrites the draft using its own feedback into a polished report."),
]
step_cols = st.columns(5)
for c, (icon, bg, title, desc) in zip(step_cols, steps):
    with c:
        st.markdown(
            f"""<div class="step-card">
                <div class="step-icon" style="background:{bg}">{icon}</div>
                <h4>{title}</h4><p>{desc}</p>
            </div>""",
            unsafe_allow_html=True,
        )

st.write("")
st.write("")

# ---------------------------------------------------------------------------
# Run pipeline
# ---------------------------------------------------------------------------

if run_clicked:
    if not topic_input or not topic_input.strip():
        st.warning("Please enter a topic before starting.")
    else:
        topic = topic_input.strip()
        status_box = st.status("Waking up the agents...", expanded=True)
        try:
            with status_box:
                result_state = run_pipeline(topic, status_box)
            st.session_state.result = result_state
            st.session_state.topic = topic
            st.session_state.history.append(
                {
                    "topic": topic,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "state": result_state,
                }
            )
        except Exception as e:
            status_box.update(label="Research failed", state="error")
            st.error(f"Something went wrong while running the pipeline: {e}")

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

if st.session_state.result:
    state = st.session_state.result
    st.markdown('<div class="section-title" style="margin-top:40px;">Your report</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">{st.session_state.topic}</div>', unsafe_allow_html=True)

    tab_final, tab_draft, tab_critique, tab_research = st.tabs(
        ["✅  Final Report", "📝  Draft", "🧠  Critique", "📚  Raw Research"]
    )

    with tab_final:
        card(state.get("final_report", "_No final report available._"))
        st.write("")
        st.download_button(
            "⬇ Download final report (.md)",
            data=state.get("final_report", ""),
            file_name=f"{st.session_state.topic[:40].replace(' ', '_')}_report.md",
            mime="text/markdown",
        )

    with tab_draft:
        card(state.get("report", "_No draft available._"))

    with tab_critique:
        card(state.get("improvements", "_No critique available._"))

    with tab_research:
        with st.expander("Search results", expanded=False):
            st.markdown(state.get("search_results", "_No search results._"))
        with st.expander("Scraped content", expanded=False):
            st.markdown(state.get("scraped_content", "_No scraped content._"))

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown(
    """
<div class="footer">
    <div class="brand">✦ Nova<span class="dot">.</span></div>
    <div>Multi-agent deep research, built on LangChain &amp; Streamlit.</div>
    <div class="footer-links">
        <a href="#how-it-works">How it works</a>
        <a href="#try-it">Try it</a>
    </div>
</div>
""",
    unsafe_allow_html=True,
)