import os
from datetime import datetime
from html import escape
from typing import Any

import requests
import streamlit as st

st.set_page_config(
    page_title="PhishGuard | Email Security",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
MAX_EMAIL_FILES = 10  # Safety limit per batch; requests are sent sequentially.

# ------------------------------- Design system -------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --bg:#080f1d; --surface:#101b2d; --surface2:#142239; --line:rgba(148,163,184,.16);
            --text:#edf4ff; --muted:#91a3bc; --blue:#4f8cff; --cyan:#55d6e8; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    .stApp { background:radial-gradient(ellipse at 80% 0%,rgba(37,99,235,.13),transparent 34%),var(--bg); color:var(--text); }
    [data-testid="stHeader"] { background:rgba(8,15,29,.82); }
    [data-testid="stSidebar"] { background:#0b1526; border-right:1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { padding-top:1.5rem; }
    .brand { display:flex; align-items:center; gap:12px; padding:8px 5px 22px; }
    .brand-icon { width:42px;height:42px;border-radius:13px;display:grid;place-items:center;
        background:linear-gradient(145deg,#2563eb,#0e7490);font-size:22px;box-shadow:0 8px 25px #2563eb40; }
    .brand-name { font:700 21px 'Space Grotesk'; color:#f8fbff; letter-spacing:-.5px; }
    .brand-sub { color:var(--muted);font-size:11px;letter-spacing:1.5px;text-transform:uppercase; }
    .eyebrow { color:#6dd9ed;font-size:11px;font-weight:700;letter-spacing:2.2px;text-transform:uppercase;margin-bottom:12px; }
    .hero { padding:34px 38px; border:1px solid rgba(105,151,218,.23); border-radius:23px;
        background:linear-gradient(115deg,rgba(24,43,71,.97),rgba(13,25,44,.94));
        box-shadow:0 20px 60px rgba(0,0,0,.18); position:relative; overflow:hidden; margin-bottom:25px; }
    .hero:after { content:' ';position:absolute;width:260px;height:260px;border:1px solid #60a5fa22;border-radius:50%;right:-65px;top:-120px;box-shadow:0 0 0 35px #60a5fa08,0 0 0 70px #60a5fa06; }
    .hero h1 { font:700 clamp(30px,4vw,46px)/1.12 'Space Grotesk';letter-spacing:-1.5px;color:#f8fbff;margin:0; }
    .hero p { color:#a9bad1;font-size:15px;line-height:1.7;max-width:730px;margin:14px 0 0; }
    .section-title { font:600 21px 'Space Grotesk';color:#f2f7ff;margin:8px 0 4px; }
    .section-copy { color:var(--muted);font-size:13px;margin-bottom:18px; }
    .card { background:linear-gradient(145deg,rgba(18,32,53,.96),rgba(13,25,43,.96));border:1px solid var(--line);
        border-radius:17px;padding:20px 21px;height:100%; }
    .card-label { color:#91a5c0;font-size:11px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase; }
    .card-value { font:700 30px 'Space Grotesk';color:#f3f7ff;margin-top:8px; }
    .card-hint { color:#8194ae;font-size:12px;margin-top:3px; }
    .status-dot { display:inline-block;width:8px;height:8px;border-radius:50%;background:#34d399;margin-right:7px;box-shadow:0 0 12px #34d39988; }
    .status-dot.off { background:#fb7185;box-shadow:0 0 12px #fb718588; }
    .result { border-radius:18px;padding:24px 26px;border:1px solid var(--line);margin:12px 0 18px; }
    .result.bad { background:linear-gradient(110deg,#451d2b66,#121e31);border-color:#fb718566; }
    .result.good { background:linear-gradient(110deg,#12463866,#121e31);border-color:#34d39966; }
    .result-kicker { color:#a8b8ce;font-size:11px;font-weight:700;letter-spacing:1.6px;text-transform:uppercase; }
    .result-name { font:700 34px 'Space Grotesk';color:#fff;margin:7px 0 3px; }
    .muted { color:var(--muted);font-size:13px;line-height:1.65; }
    .step { display:flex;gap:12px;align-items:flex-start;margin:13px 0;color:#aabbd0;font-size:13px; }
    .step-n { flex:0 0 25px;height:25px;border-radius:8px;background:#1d3b63;color:#8bc5ff;display:grid;place-items:center;font-weight:700; }
    div.stButton > button { border:1px solid #3979e9;border-radius:11px;min-height:45px;font-weight:700;color:white;
        background:linear-gradient(100deg,#2563eb,#087eaa);transition:.18s ease; }
    div.stButton > button:hover { border-color:#69b4ff;color:white;filter:brightness(1.12);transform:translateY(-1px); }
    [data-testid="stFileUploader"] section { background:#101e32;border:1px dashed #4777a8;border-radius:14px; }
    [data-testid="stMetric"] { background:#122139;border:1px solid var(--line);padding:13px 15px;border-radius:13px; }
    [data-testid="stMetricLabel"] { color:#9db0c9; }
    [data-testid="stMetricValue"] { color:#f5f8ff; }
    [data-testid="stRadio"] label { color:#c3d0e2; }
    [data-testid="stExpander"] { border:1px solid var(--line);border-radius:12px;background:#0f1b2d; }
    hr { border-color:var(--line); }
    .footer { text-align:center;color:#71839c;font-size:11px;padding:28px 0 8px;letter-spacing:.3px; }
    .pill { display:inline-block;padding:5px 10px;border-radius:20px;background:#183454;color:#8ecbff;font-size:11px;font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------- API helpers ---------------------------------
def check_api_health(api_url: str) -> dict[str, Any] | None:
    try:
        response = requests.get(f"{api_url.rstrip('/')}/health", timeout=4)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else None
    except (requests.RequestException, ValueError):
        return None


def predict_email(api_url: str, filename: str, file_bytes: bytes) -> dict[str, Any]:
    response = requests.post(
        f"{api_url.rstrip('/')}/predict",
        files={"email_file": (filename, file_bytes, "message/rfc822")},
        timeout=(10, 180),
    )
    try:
        payload = response.json()
    except ValueError:
        payload = {"detail": response.text or "The API returned an unreadable response."}
    if not response.ok:
        detail = payload.get("detail", payload) if isinstance(payload, dict) else payload
        raise RuntimeError(f"API error ({response.status_code}): {detail}")
    if not isinstance(payload, dict):
        raise RuntimeError("The API response was not a JSON object.")
    missing = {"prediction", "classification", "decision_score"}.difference(payload)
    if missing:
        raise RuntimeError(f"API response is missing: {', '.join(sorted(missing))}")
    return payload


if "scan_history" not in st.session_state:
    st.session_state.scan_history = []
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None
if "last_batch_results" not in st.session_state:
    st.session_state.last_batch_results = []

# ---------------------------------- Sidebar -----------------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-icon">🛡️</div><div><div class="brand-name">PhishGuard</div><div class="brand-sub">Email threat intelligence</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div class='muted' style='font-weight:700;margin-bottom:8px'>WORKSPACE</div>", unsafe_allow_html=True)
    page = st.radio("Navigation", ["Dashboard", "Email Scanner", "About PhishGuard"], label_visibility="collapsed", key="nav_page")
    st.markdown("---")
    st.markdown("<div class='muted' style='font-weight:700;margin-bottom:8px'>BACKEND CONNECTION</div>", unsafe_allow_html=True)
    api_url = st.text_input("FastAPI base URL", value=DEFAULT_API_URL, help="Base URL only. Do not add /health or /predict.").strip().rstrip("/")
    if not api_url:
        api_url = DEFAULT_API_URL
    health = check_api_health(api_url)
    api_ok = bool(health and health.get("status") == "healthy")
    st.markdown(
        f"<div class='muted'><span class='status-dot {' ' if api_ok else 'off'}'></span>{'API connected' if api_ok else 'API unavailable'}</div>",
        unsafe_allow_html=True,
    )
    if api_ok:
        st.caption(f"Preprocessor · {'Ready' if health.get('preprocessor_loaded') else 'Not loaded'}")
        st.caption(f"SGD classifier · {'Ready' if health.get('classifier_loaded') else 'Not loaded'}")
    else:
        st.caption("Start FastAPI to enable email scanning.")
    st.markdown("---")
    st.caption("SUPPORTED FORMAT")
    st.markdown("`.eml` · RFC 5322 email")
    st.caption("MODEL")
    st.markdown("`SGDClassifier` · linear classifier")
    st.markdown("<div class='footer'>PHISHGUARD · VERSION 2.0</div>", unsafe_allow_html=True)

# --------------------------------- Dashboard ----------------------------------
if page == "Dashboard":
    st.markdown(
        "<div class='hero'><div class='eyebrow'>SECURITY OPERATIONS CENTER&nbsp; / &nbsp;EMAIL PROTECTION</div><h1>See threats before<br>they reach your inbox.</h1><p>PhishGuard analyzes uploaded email messages using a machine-learning pipeline to identify phishing attempts and legitimate communication.</p></div>",
        unsafe_allow_html=True,
    )
    history = st.session_state.scan_history
    total = len(history)
    phishing = sum(item["prediction"] == 1 for item in history)
    legitimate = total - phishing
    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, hint in [
        (c1, "EMAILS ANALYZED", total, "This session"),
        (c2, "PHISHING DETECTED", phishing, "Flagged by the model"),
        (c3, "LEGITIMATE", legitimate, "Classified as legitimate"),
        (c4, "API STATUS", "ONLINE" if api_ok else "OFFLINE", "FastAPI service"),
    ]:
        with col:
            st.markdown(f"<div class='card'><div class='card-label'>{label}</div><div class='card-value'>{value}</div><div class='card-hint'>{hint}</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Security workspace</div><div class='section-copy'>Choose a task to continue.</div>", unsafe_allow_html=True)
    left, right = st.columns([1.2, 1], gap="large")
    with left:
        st.markdown("<div class='card'><span class='pill'>PRIMARY ACTION</span><div class='section-title'>Scan an email</div><p class='muted'>Upload an .eml message and run it through the connected phishing detection model.</p></div>", unsafe_allow_html=True)
        def open_email_scanner():
            st.session_state.nav_page = "Email Scanner"

        st.button("Open email scanner →", use_container_width=True, on_click=open_email_scanner)
    with right:
        st.markdown("<div class='card'><div class='card-label'>DETECTION PIPELINE</div><div class='step'><span class='step-n'>01</span><span><b>Parse message</b><br>Read headers, body and attachments.</span></div><div class='step'><span class='step-n'>02</span><span><b>Extract features</b><br>Generate the 18 model input features.</span></div><div class='step'><span class='step-n'>03</span><span><b>Transform & classify</b><br>Apply preprocessing and SGD classification.</span></div><div class='step'><span class='step-n'>04</span><span><b>Return result</b><br>Display the predicted email category.</span></div></div>", unsafe_allow_html=True)
    if history:
        st.markdown("<div class='section-title'>Recent activity</div><div class='section-copy'>Analysis performed during this browser session.</div>", unsafe_allow_html=True)
        st.dataframe(
            [{"Email": x["filename"], "Classification": x["classification"], "Decision score": f'{x["decision_score"]:.5f}', "Time": x["time"]} for x in reversed(history[-8:])],
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("No emails have been scanned in this session. Start with the Email Scanner to see activity here.")

# -------------------------------- Email scanner -------------------------------
elif page == "Email Scanner":
    st.markdown("<div class='eyebrow'>THREAT ANALYSIS / FILE INSPECTION</div><div class='section-title' style='font-size:30px'>Email scanner</div><div class='section-copy'>Submit an email file for machine-learning analysis.</div>", unsafe_allow_html=True)
    scan_col, guide_col = st.columns([1.35, .85], gap="large")
    with scan_col:
        st.markdown("<div class='card'><div class='section-title'>Upload email message</div><p class='muted'>Select an RFC 5322 <code>.eml</code> file. The file is sent to your configured FastAPI backend for analysis.</p>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Choose .eml files",
            type=["eml"],
            accept_multiple_files=True,
            help=f"Select up to {MAX_EMAIL_FILES} .eml files. Each file is submitted separately to the existing API.",
        )
        file_count = len(uploaded_files) if uploaded_files else 0
        if uploaded_files:
            total_size_kb = sum(len(item.getvalue()) for item in uploaded_files) / 1024
            st.markdown(
                f"<div class='muted'>Selected: <b>{file_count}</b> / {MAX_EMAIL_FILES} files &nbsp;·&nbsp; Combined size: {total_size_kb:,.1f} KB</div>",
                unsafe_allow_html=True,
            )
            with st.expander("Review selected files"):
                for item in uploaded_files:
                    st.write(f"📄 {item.name} · {len(item.getvalue()) / 1024:,.1f} KB")
        too_many_files = file_count > MAX_EMAIL_FILES
        if too_many_files:
            st.error(f"You selected {file_count} files. The maximum per batch is {MAX_EMAIL_FILES}.")
        run_scan = st.button(
            f"🔍  Analyze {file_count} email(s)",
            type="primary",
            disabled=file_count == 0 or too_many_files or not api_ok,
            use_container_width=True,
        )
        st.markdown(
            "<p class='muted' style='font-size:11px'>Files are analyzed sequentially, one API request per email. Upload only messages you are authorized to inspect. Files are not saved to the frontend project folder.</p></div>",
            unsafe_allow_html=True,
        )
    with guide_col:
        st.markdown("<div class='card'><div class='card-label'>BEFORE YOU SCAN</div><div class='step'><span class='step-n'>✓</span><span>Use emails saved as <b>.eml</b>.</span></div><div class='step'><span class='step-n'>✓</span><span>Select up to 10 files per batch.</span></div><div class='step'><span class='step-n'>✓</span><span>Do not upload confidential messages to an untrusted API host.</span></div></div>", unsafe_allow_html=True)
    if not api_ok:
        st.warning("FastAPI is not healthy. Start the backend and check the API URL in the sidebar.")
    elif health.get("preprocessor_loaded") is False or health.get("classifier_loaded") is False:
        st.error("The API is running, but the preprocessor or classifier is not loaded.")
    if run_scan and uploaded_files:
        batch_results = []
        progress = st.progress(0, text="Preparing batch analysis...")
        for index, uploaded in enumerate(uploaded_files, start=1):
            try:
                progress.progress((index - 1) / len(uploaded_files), text=f"Analyzing {uploaded.name} ({index}/{len(uploaded_files)})...")
                result = predict_email(api_url, uploaded.name, uploaded.getvalue())
                result["filename"] = uploaded.name
                result["status"] = "Completed"
                batch_results.append(result)
                st.session_state.last_prediction = result
                st.session_state.scan_history.append({
                    "filename": uploaded.name,
                    "classification": result["classification"],
                    "prediction": int(result["prediction"]),
                    "decision_score": float(result["decision_score"]),
                    "time": datetime.now().strftime("%H:%M:%S"),
                })
            except requests.Timeout:
                batch_results.append({"filename": uploaded.name, "status": "Failed", "error": "Request timed out."})
            except requests.ConnectionError:
                batch_results.append({"filename": uploaded.name, "status": "Failed", "error": "Could not connect to FastAPI."})
            except Exception as exc:
                batch_results.append({"filename": uploaded.name, "status": "Failed", "error": str(exc)})
            progress.progress(index / len(uploaded_files), text=f"Processed {index}/{len(uploaded_files)} files")
        progress.empty()
        st.session_state.last_batch_results = batch_results
        succeeded = sum(item.get("status") == "Completed" for item in batch_results)
        failed = len(batch_results) - succeeded
        if failed:
            st.warning(f"Batch finished: {succeeded} completed, {failed} failed.")
        else:
            st.success(f"Batch analysis completed successfully for all {succeeded} emails.")

    batch_results = st.session_state.get("last_batch_results", [])
    if batch_results:
        st.markdown("---")
        st.markdown("<div class='section-title'>Batch analysis report</div><div class='section-copy'>Results for the most recently submitted batch.</div>", unsafe_allow_html=True)
        completed = [item for item in batch_results if item.get("status") == "Completed"]
        phishing_count = sum(int(item.get("prediction", 0)) == 1 for item in completed)
        legitimate_count = len(completed) - phishing_count
        m1, m2, m3 = st.columns(3)
        m1.metric("Files submitted", len(batch_results))
        m2.metric("Phishing detected", phishing_count)
        m3.metric("Legitimate", legitimate_count)
        rows = [{
            "Email file": item["filename"],
            "Status": item.get("status", "Unknown"),
            "Classification": item.get("classification", item.get("error", "—")),
            "Decision score": f'{item["decision_score"]:.5f}' if isinstance(item.get("decision_score"), (int, float)) else "—",
        } for item in batch_results]
        st.dataframe(rows, use_container_width=True, hide_index=True)
        for item in batch_results:
            with st.expander(f"{item['filename']} · {item.get('classification', item.get('status', 'Result'))}"):
                if item.get("status") == "Completed":
                    is_phishing = int(item.get("prediction", 0)) == 1
                    kind = "bad" if is_phishing else "good"
                    icon = "⚠️" if is_phishing else "✓"
                    label = "Phishing detected" if is_phishing else "Likely legitimate"
                    st.markdown(f"<div class='result {kind}'><div class='result-kicker'>CLASSIFICATION RESULT</div><div class='result-name'>{icon} {label}</div><div class='muted'>File: {escape(str(item['filename']))}</div></div>", unsafe_allow_html=True)
                    a, b, c = st.columns(3)
                    a.metric("Prediction label", str(item.get("prediction", "—")))
                    b.metric("Input features", str(item.get("input_features", "—")))
                    c.metric("Encoded features", str(item.get("encoded_features", "—")))
                    st.caption(f"SGD decision score: {item.get('decision_score', 0):.6f} (not a probability)")
                    with st.expander("Technical API response"):
                        st.json(item)
                else:
                    st.error(item.get("error", "Analysis failed."))
        st.download_button(
            "Download batch report (JSON)",
            data=__import__("json").dumps(batch_results, indent=2),
            file_name="phishguard_batch_analysis.json",
            mime="application/json",
        )
        if st.button("Clear batch results"):
            st.session_state.last_batch_results = []
            st.session_state.last_prediction = None
            st.rerun()

# ----------------------------------- About ------------------------------------
else:
    st.markdown("<div class='eyebrow'>PRODUCT OVERVIEW</div><div class='section-title' style='font-size:30px'>About PhishGuard</div><div class='section-copy'>A machine-learning application for email threat classification.</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero'><div class='eyebrow'>EMAIL SECURITY · MACHINE LEARNING</div><h1>Understand the signal.<br>Spot the threat.</h1><p>PhishGuard accepts .eml files, extracts structural and content-related features, transforms them using the saved preprocessing pipeline, and classifies the message with a trained SGD classifier.</p></div>", unsafe_allow_html=True)
    x, y = st.columns(2, gap="large")
    with x:
        st.markdown("<div class='card'><div class='section-title'>Technology stack</div><div class='step'><span class='step-n'>01</span><span><b>Streamlit</b><br>Interactive frontend and session dashboard.</span></div><div class='step'><span class='step-n'>02</span><span><b>FastAPI</b><br>Backend endpoints for health checks and prediction.</span></div><div class='step'><span class='step-n'>03</span><span><b>Scikit-learn</b><br>Saved preprocessor and SGD classifier.</span></div><div class='step'><span class='step-n'>04</span><span><b>Python email parser</b><br>Reads email headers, bodies and attachments.</span></div></div>", unsafe_allow_html=True)
    with y:
        st.markdown("<div class='card'><div class='section-title'>Prediction workflow</div><div class='step'><span class='step-n'>1</span><span>Upload an .eml file to the frontend.</span></div><div class='step'><span class='step-n'>2</span><span>FastAPI parses the email and extracts 18 features.</span></div><div class='step'><span class='step-n'>3</span><span>The preprocessor transforms the feature row.</span></div><div class='step'><span class='step-n'>4</span><span>The SGD classifier returns a class and decision score.</span></div></div>", unsafe_allow_html=True)

st.markdown("<div class='footer'>PHISHGUARD · EMAIL THREAT ANALYSIS · STREAMLIT + FASTAPI</div>", unsafe_allow_html=True)
