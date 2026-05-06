import streamlit as st
from streamlit_option_menu import option_menu
from student_panel import student_panel
from admin_panel import admin_panel

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Student System", layout="wide")
st.markdown("""
<style>
div.stButton > button {
    background-color: green;
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    border: none;
}
div.stButton > button:hover {
    background-color: #fb8c00;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# SESSION STATE
# -----------------------------
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False

# -----------------------------
# SIDEBAR MENU
# -----------------------------
with st.sidebar:
    selected = option_menu(
        menu_title="Menu",
        options=["Home", "Admin", "Student"],
        icons=["house", "person", "mortarboard"],
        menu_icon="menu-button-wide",
        default_index=0,
     styles={
            "container": {
                "padding": "5px",
                "background-color": "lightwhite"
            },
            "icon": {
                "color": "#38bdf8",
                "font-size": "20px"
            },
            "nav-link": {
                "font-size": "18px",
                "text-align": "left",
                "margin": "5px",
                "color": "black",
                "border-radius": "8px"
            },
            "nav-link-selected": {
                "background-color": "#1e293b",
                "color": "white",
                "font-weight": "bold"
            }
        }
    )


# -----------------------------
# HOME
# -----------------------------
if selected == "Home":
    
    st.markdown("""
<style>


/* Animated background */
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.main {
    background: linear-gradient(-45deg,  #1e293b,  #38bdf8, #2563eb, #1e3a8a);
    background-size: 400% 400%;
    animation: gradientBG 10s ease infinite;
    padding: 60px;
    border-radius: 20px;
    text-align: center;
    color: white;
}

/* Fade-in animation */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(20px);}
    to {opacity: 1; transform: translateY(0);}
}

.title {
    font-size: 52px;
    font-weight: bold;
    animation: fadeIn 1.5s ease-in-out;
}

.subtitle {
    font-size: 22px;
    margin-top: 15px;
    animation: fadeIn 2s ease-in-out;
}

.button {
    margin-top: 30px;
    padding: 12px 25px;
    background: white;
    color: #333;
    border-radius: 8px;
    display: inline-block;
    font-weight: bold;
    animation: fadeIn 2.5s ease-in-out;
    cursor: pointer;
}

.button:hover {
    background: #f1f1f1;
                }
/* Apply font */
.title {
    font-size: 52px;
    font-weight: bold;
    font-family: 'Poppins', sans-serif;
}
.subtitle {
    font-family: 'Poppins', sans-serif;
}

</style>

<div class="main">
    <div class="title">🎓 Student Performance Analysis </div>
    <div class="subtitle">📊 Monitor | 📋 Evaluate | 🚀 Enhance Student Performance</div>
    <div class="button"> Select Role </div>
</div>
""", unsafe_allow_html=True)
# -----------------------------
# ADMIN
# -----------------------------
elif selected == "Admin":
    st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: "#38bdf8";
    
}

/* Card effect */
.block-container {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
}
</style>
""", unsafe_allow_html=True)
    st.title("🎓 Student Performance analysis")

    if "logout_msg" in st.session_state:
        
        st.success(st.session_state["logout_msg"])
        del st.session_state["logout_msg"]

    if "login_msg" in st.session_state:
        st.success(st.session_state["login_msg"])
        del st.session_state["login_msg"]

    ADMIN_USER = "admin"
    ADMIN_PASS = "1234"

    if not st.session_state["admin_logged_in"]:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state["admin_logged_in"] = True
                st.session_state["login_msg"] = "Login Successfully ✅"
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

    else:
        admin_panel()

# -----------------------------
# STUDENT
# -----------------------------
elif selected == "Student":
    st.title("🎓 Student Performance analysis")
    student_panel()

