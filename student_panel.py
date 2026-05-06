import streamlit as st
import pandas as pd
import os
from chatbot import chatbot_response
from streamlit_option_menu import option_menu

def student_panel():

    st.title("🧑‍🎓 Student Panel")

    # -----------------------------
    # LOAD DATA
    # -----------------------------
    if os.path.exists("main_dataset.csv"):
        data = pd.read_csv("main_dataset.csv")
    elif os.path.exists("main_dataset.xlsx"):
        data = pd.read_excel("main_dataset.xlsx")
    else:
        st.error("🚫 No dataset uploaded by Admin")
        st.stop()

    data.columns = data.columns.str.strip()
    data = data.astype(str).apply(lambda x: x.str.strip())

    # -----------------------------
    # LOGIN
    # -----------------------------
    st.subheader("🔍 Login")
    sid = st.text_input("Enter Student ID / Roll No")

    if not sid:
        st.stop()

    id_cols = [col for col in data.columns if "id" in col.lower() or "roll" in col.lower()]

    if not id_cols:
        st.error("❌ No ID column found")
        st.stop()

    id_col = id_cols[0]

    student = data[data[id_col].str.lower() == sid.strip().lower()]

    if student.empty:
        st.error("❌ Student not found")
        st.stop()

    st.success(f"Welcome {sid} ✅")

    # -----------------------------
    # MENU
    # -----------------------------
    selected = option_menu(
        menu_title=None,
        options=["Result", "Grievance", "AI Chatbot"],
        icons=["bar-chart", "chat", "robot"],
        orientation="horizontal",
        styles={
        "container": {
            "padding": "10px",
            "background-color": "#0f172a",
            "border-radius": "15px",
            "box-shadow": "0px 4px 12px rgba(0,0,0,0.4)"
        },

        "nav-link": {
            "font-size": "15px",
            "font-weight": "500",
            "color": "#cbd5e1",
            "text-align": "center",
            "margin": "5px",
            "padding": "12px",
            "border-radius": "12px",
            "transition": "all 0.3s ease",
        },

        "nav-link:hover": {
            "background-color": "#1e293b",
            "color": "white",
            "transform": "scale(1.05)"
        },

        "nav-link-selected": {
            "background": "linear-gradient(90deg, #2563eb, #3b82f6)",
            "color": "white",
            "font-weight": "600",
            "border-radius": "12px",
            "box-shadow": "0px 0px 10px rgba(37, 99, 235, 0.7)"
        },

        "icon": {
            "color": "#38bdf8",
            "font-size": "18px"
        }
    }

    
    )

    # -----------------------------
    # RESULT TAB
    # -----------------------------
    if selected == "Result":

        st.subheader("📌 Student Details")
        st.dataframe(student)

        # -----------------------------
        # ADMIN LOGIC
        # -----------------------------
        admin_data = data.copy()

        def num(col):
            return pd.to_numeric(admin_data[col], errors="coerce") if col in admin_data.columns else 0

        model_data = pd.DataFrame()
        model_data["Student_ID"] = admin_data[id_col]

        model_data["CGPA"] = num("CGPA")
        model_data["Attendance"] = num("Attendance")
        model_data["Backlogs"] = num("Backlogs")
        model_data["Total_Marks"] = num("Total_Marks")
        model_data["Internships"] = num("Internships")
        model_data["Activity_Score"] = num("Activity_Score")

        model_data["Communication"] = admin_data["Communication Skills"].astype(str).str.lower().map({
            "basic": 1, "intermediate": 2, "good": 3
        }).fillna(2)

        model_data["Study_Hours"] = num("How many hour do you study daily?")
        model_data["Skill_Hours"] = num("How many hour do you spent daily on your skill development?")

        model_data["Sports_Level"] = admin_data["Sports_Level"].astype(str).str.lower().map({
            "college": 1, "district": 2, "state": 3
        }).fillna(1)

        model_data = model_data.fillna(model_data.median(numeric_only=True))

        # -----------------------------
        # LEVEL LOGIC
        # -----------------------------
        def academic_score(row):
            score = 0
            if row["CGPA"] >= 8: score += 2
            elif row["CGPA"] >= 6.5: score += 1

            if row["Attendance"] >= 85: score += 2
            elif row["Attendance"] >= 70: score += 1

            if row["Backlogs"] == 0: score += 2
            elif row["Backlogs"] == 1: score += 1

            if row["Total_Marks"] >= 75: score += 2
            elif row["Total_Marks"] >= 60: score += 1

            return "Best" if score >= 6 else "Moderate" if score >= 3 else "Risk"

        def skill_score(row):
            score = 0
            if row["Communication"] >= 2: score += 2

            if row["Study_Hours"] >= 3: score += 2
            elif row["Study_Hours"] >= 2: score += 1

            if row["Skill_Hours"] >= 2: score += 2
            elif row["Skill_Hours"] >= 1: score += 1

            return "Best" if score >= 5 else "Moderate" if score >= 3 else "Risk"

        def growth_score(row):
            score = 0
            if row["Internships"] >= 2: score += 2
            elif row["Internships"] == 1: score += 1

            if row["Activity_Score"] >= 2: score += 2
            elif row["Activity_Score"] >= 1: score += 1

            if row["Sports_Level"] >= 2: score += 1

            return "Best" if score >= 4 else "Moderate" if score >= 2 else "Risk"

        def final_performance(row):
            levels = [row["Academic_Level"], row["Skill_Level"], row["Growth_Level"]]
            if levels.count("Best") >= 2:
                return "Best"
            elif levels.count("Risk") >= 2:
                return "Risk"
            else:
                return "Moderate"

        model_data["Academic_Level"] = model_data.apply(academic_score, axis=1)
        model_data["Skill_Level"] = model_data.apply(skill_score, axis=1)
        model_data["Growth_Level"] = model_data.apply(growth_score, axis=1)
        model_data["Performance"] = model_data.apply(final_performance, axis=1)

        model_data["Suggestion"] = model_data["Performance"].apply(
            lambda x: "Improve Immediately" if x == "Risk" else "Maintain"
        )

        # -----------------------------
        # FILTER STUDENT
        # -----------------------------
        student_report = model_data[
            model_data["Student_ID"].str.lower() == sid.strip().lower()
        ]

        if student_report.empty:
            st.error("❌ No report found")
        else:
            st.subheader("📊 Final Performance Report")
            communication_map = {1: "Basic", 2: "Intermediate", 3: "Good"}
            sports_map = {1: "College", 2: "District", 3: "State"}

            student_report["Communication"] = student_report["Communication"].map(communication_map)
            student_report["Sports_Level"] = student_report["Sports_Level"].map(sports_map)

            st.dataframe(student_report)

            row = student_report.iloc[0]

            # -----------------------------
            # ATTENDANCE ALERT
            # -----------------------------
            if row["Attendance"] < 50:
                st.error(f"🚨 Very Low Attendance: {row['Attendance']}%")
            elif row["Attendance"] < 75:
                st.warning(f"⚠️ Low Attendance: {row['Attendance']}%")
            else:
                st.success(f"✅ Good Attendance: {row['Attendance']}%")

            # -----------------------------
            # 🎯 PERFORMANCE-BASED RECOMMENDATIONS
            # -----------------------------
            st.subheader("📢 Personalized Recommendations")

            rec = []

            if row["Performance"] == "Risk":
                rec += [
                    "🚨 Your performance is at RISK level",
                    "📚 Attend all classes regularly (min 75%)",
                    "📖 Study daily 3–4 hours",
                    "❌ Clear backlogs immediately",
                    "🧠 Improve communication & technical skills",
                    "👨‍🏫 Meet faculty/mentor",
                    "🚀 Participate in activities"
                ]

            elif row["Performance"] == "Moderate":
                rec += [
                    "⚠️ Your performance is MODERATE",
                    "📘 Improve CGPA above 8",
                    "📅 Maintain attendance above 80%",
                    "💡 Improve coding & communication",
                    "📈 Do internships & activities",
                    "🎯 Convert weak areas into strengths"
                ]

            else:
                rec += [
                    "🌟 Excellent Performance!",
                    "🏆 Maintain consistency",
                    "🚀 Apply for internships/projects",
                    "🎤 Improve leadership skills",
                    "📊 Aim for placements/certifications",
                    "🔥 Help other students"
                ]

            # Extra Alerts
            if row["Academic_Level"] == "Risk":
                rec.append("📚 Academic Alert: Focus more on subjects")

            if row["Skill_Level"] == "Risk":
                rec.append("🧠 Skill Alert: Improve communication & skills")

            if row["Growth_Level"] == "Risk":
                rec.append("🚀 Growth Alert: Participate more")

            for r in rec:
                st.write("•", r)

    # -----------------------------
    # GRIEVANCE
    # -----------------------------
    elif selected == "Grievance":

        fb = st.text_area("Write your Grievance")

        if st.button("Submit Grievance"):
            if fb.strip():
                new = pd.DataFrame([{"Student_ID": sid, "Grievance": fb}])

                if os.path.exists("grievance.csv"):
                    g = pd.read_csv("grievance.csv")
                    g = pd.concat([g, new], ignore_index=True)
                else:
                    g = new

                g.to_csv("grievance.csv", index=False)
                st.success("✅ Submitted")
            else:
                st.warning("Enter grievance")

    # -----------------------------
    # CHATBOT
    # -----------------------------
    elif selected == "AI Chatbot":

        st.subheader("🤖 AI Assistant")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for sender, text in st.session_state.chat_history:
            st.write(f"**{sender}:** {text}")

        msg = st.chat_input("Ask something...")

        if msg:
            response = chatbot_response(sid, msg)
            st.session_state.chat_history.append(("You", msg))
            st.session_state.chat_history.append(("AI", response))
            st.rerun()