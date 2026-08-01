import sys
import os
import streamlit as st

# ---------------------------------------------------------------------------
# Add all SmartFM subfolders to Python path so imports work correctly
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for subfolder in ("managers", "models", "utils", "ui"):
    path = os.path.join(BASE_DIR, subfolder)
    if path not in sys.path:
        sys.path.insert(0, path)

# ---------------------------------------------------------------------------
# Page config — must be the FIRST streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SmartFM — Smart Fleet Management",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# Custom CSS — dark mode styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1a1d27; border-right: 1px solid #2d3147; }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    [data-testid="stSuccess"] { background-color: #1a3a2a; border-left: 4px solid #00c853; }
    [data-testid="stError"]   { background-color: #3a1a1a; border-left: 4px solid #ff1744; }
    [data-testid="stWarning"] { background-color: #3a2e1a; border-left: 4px solid #ffc107; }
    [data-testid="stInfo"]    { background-color: #1a2a3a; border-left: 4px solid #2196f3; }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1e2130 !important;
        color: #ffffff !important;
        border: 1px solid #2d3147 !important;
        border-radius: 6px !important;
    }
    .stButton > button {
        background-color: #2d6df6; color: white;
        border: none; border-radius: 6px;
        padding: 0.5rem 1.5rem; font-weight: 600;
    }
    .stButton > button:hover { background-color: #1a56d6; color: white; }
    [data-testid="metric-container"] {
        background-color: #1e2130;
        border: 1px solid #2d3147;
        border-radius: 8px; padding: 1rem;
    }
    h1, h2, h3 { color: #ffffff !important; }
    .badge-pending    { background:#f59e0b; color:#000; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .badge-confirmed  { background:#3b82f6; color:#fff; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .badge-delivered  { background:#10b981; color:#fff; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .badge-cancelled  { background:#ef4444; color:#fff; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .badge-available  { background:#10b981; color:#fff; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .badge-assigned   { background:#3b82f6; color:#fff; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .badge-maintenance{ background:#ef4444; color:#fff; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .badge-unpaid     { background:#f59e0b; color:#000; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .badge-paid       { background:#10b981; color:#fff; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Bootstrap SmartFMSystem into session_state (runs once per session)
# ---------------------------------------------------------------------------
def bootstrap_system():
    """
    Initialise SmartFMSystem and store it in st.session_state.
    Streamlit reruns the script on every interaction — storing the system
    in session_state ensures managers are only created once per session.

    Returns:
        SmartFMSystem: The fully initialised system singleton.
    """
    if "smartfm_system" not in st.session_state:
        from managers.smartfm_system import SmartFMSystem
        system = SmartFMSystem()
        if not system.is_initialised:
            system.initialise()
        st.session_state["smartfm_system"] = system

    return st.session_state["smartfm_system"]


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
def render_sidebar(system) -> str:
    """
    Render the sidebar navigation panel.

    Args:
        system: The initialised SmartFM system.

    Returns:
        str: The name of the currently selected page.
    """
    with st.sidebar:
        st.markdown("## 🚚 SmartFM")
        st.markdown("**Smart Fleet Management System**")
        st.markdown("*ABC-Trans Vietnam*")
        st.divider()

        # System status
        if system.is_initialised:
            st.success("System Online")
        else:
            st.error("System Offline")

        st.divider()

        # Login status and logout button
        if st.session_state.get("logged_in"):
            username  = st.session_state.get("username", "")
            role      = st.session_state.get("role", "CUSTOMER")
            full_name = st.session_state.get("full_name", "")
            st.markdown(f"**👤 {full_name}**")
            st.markdown(f"*{username} — {role}*")
            if st.button("🚪 Logout", use_container_width=True):
                for key in ["logged_in", "username", "role", "full_name", "user_id"]:
                    st.session_state.pop(key, None)
                st.session_state["selected_page"] = "🏠  Home"
                st.rerun()
            st.divider()

        # Build navigation pages based on role
        role = st.session_state.get("role", "")
        if not st.session_state.get("logged_in"):
            pages = ["🏠  Home", "👤  Customer Account Management"]
        elif role == "CUSTOMER":
            pages = [
                "🏠  Home",
                "👤  Customer Account Management",
                "📦  Place Shipment Order",
                "💳  Process Payment & Receipt",
            ]
        else:
            pages = [
                "🏠  Home",
                "👤  Customer Account Management",
                "📦  Place Shipment Order",
                "🚛  Fleet Dispatch",
                "💳  Process Payment & Receipt",
                "🔍  Data Inspector",
            ]

        # Initialise selected page in session state
        if "selected_page" not in st.session_state:
            st.session_state["selected_page"] = pages[0]

        # Make sure selected page still exists for current role
        if st.session_state["selected_page"] not in pages:
            st.session_state["selected_page"] = pages[0]

        st.markdown("### 📋 Navigation")
        for page in pages:
            if page == st.session_state["selected_page"]:
                st.markdown(
                    f"<div style='background:#2d6df6;padding:8px 12px;"
                    f"border-radius:6px;margin:2px 0;font-weight:600;"
                    f"color:white'>{page}</div>",
                    unsafe_allow_html=True
                )
            else:
                if st.button(page, use_container_width=True, key=f"nav_{page}"):
                    st.session_state["selected_page"] = page
                    st.rerun()

        st.divider()
        st.markdown(
            "<small>SWE30003 — Assignment 3<br>Group HN13 | May 2026</small>",
            unsafe_allow_html=True
        )

    return st.session_state.get("selected_page", "🏠  Home")


# ---------------------------------------------------------------------------
# Home page
# ---------------------------------------------------------------------------
def render_home() -> None:
    """Render the SmartFM home / welcome page."""
    st.markdown("# 🚚 Welcome to SmartFM")
    st.markdown("### Smart Fleet Management System")
    st.markdown("*Developed by Swinsoft Consulting for ABC-Trans Vietnam*")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    cards = [
        ("👤", "Customer Accounts", "Register and manage customer profiles"),
        ("📦", "Shipment Orders",   "Place and track shipment orders"),
        ("🚛", "Fleet Dispatch",    "Assign vehicles and drivers to orders"),
        ("💳", "Payments",          "Process payments and generate receipts"),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3, col4], cards):
        with col:
            st.markdown(
                f"<div style='background:#1e2130;padding:20px;border-radius:10px;"
                f"border:1px solid #2d3147;text-align:center'>"
                f"<h2>{icon}</h2><h4>{title}</h4>"
                f"<p style='color:#aaa'>{desc}</p></div>",
                unsafe_allow_html=True
            )

    st.divider()

    if not st.session_state.get("logged_in"):
        st.info(
            "👋 Welcome! Please go to **Customer Account Management** "
            "in the sidebar to register or log in."
        )
    else:
        full_name = st.session_state.get("full_name", "")
        role      = st.session_state.get("role", "CUSTOMER")
        st.success(
            f"✅ Welcome back, **{full_name}**! "
            f"You are logged in as **{role}**. "
            "Use the sidebar to navigate."
        )


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
def main() -> None:
    """
    Main application entry point.

    Flow:
        1. Bootstrap SmartFMSystem into session_state
        2. Render sidebar and get selected page
        3. Import and render the selected page module
    """
    # Step 1 — Bootstrap
    system = bootstrap_system()

    # Step 2 — Sidebar
    selected = render_sidebar(system)

    # Step 3 — Render page
    if "Home" in selected:
        render_home()

    elif "Customer Account" in selected:
        from ui.customer_page import render as render_customer
        render_customer(system)

    elif "Place Shipment" in selected:
        from ui.order_page import render as render_order
        render_order(system)

    elif "Fleet Dispatch" in selected:
        from ui.fleet_page import render as render_fleet
        render_fleet(system)

    elif "Process Payment" in selected:
        from ui.payment_page import render as render_payment
        render_payment(system)

    elif "Data Inspector" in selected:
        from ui.inspector_page import render as render_inspector
        render_inspector(system)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()