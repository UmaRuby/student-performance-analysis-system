import streamlit as st

import pandas as pd

import matplotlib.pyplot as plt

import seaborn as sns

import os

import smtplib

from email.mime.text import MIMEText

from sklearn.model_selection import train_test_split

from sklearn.preprocessing import StandardScaler

from sklearn.metrics import accuracy_score, confusion_matrix

from sklearn.linear_model import LogisticRegression

from sklearn.tree import DecisionTreeClassifier

from sklearn.ensemble import RandomForestClassifier

from streamlit_option_menu import option_menu

def convert_to_readable(data):
    report = data.copy()

    communication_map = {1: "Basic", 2: "Intermediate", 3: "Good"}
    sports_map = {1: "College", 2: "District", 3: "State"}

    if "Communication" in report.columns:
        report["Communication"] = report["Communication"].map(communication_map)

    if "Sports_Level" in report.columns:
        report["Sports_Level"] = report["Sports_Level"].map(sports_map)

    return report


# -----------------------------
# EMAIL FUNCTION
# -----------------------------
def send_email(to_email, student_id):

    sender_email = "kken66846@gmail.com"

    sender_password = "pqjs njml cwgo gqtq"  # 🔴 USE APP PASSWORD

    subject = "⚠️ Academic Risk Alert"

    body = f"""
    Dear Student {student_id},

    ⚠️ Your performance is categorized as RISK.

    Please improve:
    - Attendance
    - Study habits
    - Skills

    Contact your faculty immediately.

    Regards,
    Admin
    """

    msg = MIMEText(body)

    msg["Subject"] = subject

    msg["From"] = sender_email

    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.starttls()

        server.login(sender_email, sender_password)

        server.send_message(msg)

        server.quit()

        return True

    except Exception as e:
        return str(e)


# -----------------------------
# ADMIN PANEL
# -----------------------------
def admin_panel():

    st.title("🎓 Student Performance Analysis - Admin")
    

    selected_tab = option_menu(
        menu_title=None,
        options=["Upload Dataset","Previous Data" ,"Analysis", "Student Categories", "Grievance","Final Report", "Logout"],
        icons=["upload","", "bar-chart", "people","chat", "file", "logout"],
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
    # LOAD DATA (SAFE)
    # -----------------------------
    if "data" in st.session_state:
        df = st.session_state["data"]

    elif os.path.exists("main_dataset.csv"):
        df = pd.read_csv("main_dataset.csv")

    else:
        if selected_tab != "Upload Dataset":
            st.warning("Upload dataset first")
            st.stop()

        df = None

    # -----------------------------
    # UPLOAD DATA
    # -----------------------------
    if selected_tab == "Upload Dataset":

        file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

        if file:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)

            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                st.error("❌ Unsupported file format. Upload CSV or Excel.")
                st.stop()
            df.columns = df.columns.str.strip()

    # Store in session
            st.session_state["data"] = df

    # Save file locally
            if file.name.endswith(".csv"):
                df.to_csv("main_dataset.csv", index=False)

            elif file.name.endswith(".xlsx"):
                df.to_excel("main_dataset.xlsx", index=False)

            st.success("✅ Dataset Uploaded")

            st.dataframe(df.head(150))


        else:
            st.stop()
    # -----------------------------
# PREVIOUS DATASETS (ADAPTED)
# -----------------------------
    if selected_tab == "Previous Data":
        
        files = []

        if os.path.exists("main_dataset.csv"):
            files.append("main_dataset.csv")

        if os.path.exists("main_dataset.xlsx"):
            files.append("main_dataset.xlsx")
        if not files:
            st.warning("❌ No previous dataset found. Please upload first.")
            st.stop()

        selected_file = st.selectbox("Select file", files)

        # Load file
        if selected_file.endswith(".csv"):
            prev_df = pd.read_csv(selected_file)
        else:
            prev_df = pd.read_excel(selected_file)

        st.success(f"Viewing: {selected_file}")
        st.write(f"Rows: {prev_df.shape[0]} | Columns: {prev_df.shape[1]}")

        st.dataframe(prev_df, use_container_width=True)

        col1, col2, col3 = st.columns(3)

        # 🚀 VIEW ANALYSIS
        with col1:
                if st.button("🚀 View Analysis"):
                    st.session_state["data"] = prev_df.copy()
                    st.success("✅ Dataset loaded for analysis!")
                    st.rerun()

        # 🗑 DELETE FILE
        with col2:
                if st.button("🗑 Delete File"):
                    os.remove(selected_file)
                    st.success("File deleted")
                    st.rerun()

        # 📥 DOWNLOAD
        with col3:
                st.download_button(
                    "📥 Download",
                    prev_df.to_csv(index=False),
                    file_name=selected_file
                )

      
    # -----------------------------
    # PREPROCESS
    # -----------------------------
    def num(col):
        return pd.to_numeric(df[col], errors="coerce") if col in df.columns else 0

    model_data = pd.DataFrame()
    if "Student ID" in df.columns:
        model_data["Student_ID"] = df["Student ID"].astype(str).str.strip()
    elif "Roll No" in df.columns:
        model_data["Student_ID"] = df["Roll No"].astype(str).str.strip()
    elif "Stu_ID" in df.columns:
        model_data["Student_ID"] = df["Stu_ID"].astype(str).str.strip()

    else:
        st.error("❌ No Student ID column found")
        st.write("Available columns:", df.columns.tolist())
        st.stop()

    model_data["CGPA"] = num("CGPA")
    model_data["Attendance"] = num("Attendance")
    model_data["Backlogs"] = num("Backlogs")
    model_data["Total_Marks"] = num("Total_Marks")
    model_data["Internships"] = num("Internships")
    model_data["Activity_Score"] = num("Activity_Score")

    model_data["Communication"] = df["Communication Skills"].astype(str).str.lower().map({
        "basic": 1, "intermediate": 2, "good": 3
    }).fillna(2)

    model_data["Study_Hours"] = num("How many hour do you study daily?")
    model_data["Skill_Hours"] = num("How many hour do you spent daily on your skill development?")

    model_data["Sports_Level"] = df["Sports_Level"].astype(str).str.lower().map({
        "college": 1, "district": 2, "state": 3
    }).fillna(1)

    # 🔥 FIX WARNING HERE
    model_data = model_data.fillna(model_data.median(numeric_only=True))
    if st.checkbox("Show Preprocessed Dataset"):
        st.subheader("✅ Preprocessed Dataset")
        st.dataframe(model_data)

    # -----------------------------
    # CATEGORY LOGIC
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

    # -----------------------------
    # STUDENT CATEGORY + EMAIL
    # -----------------------------
    if selected_tab == "Student Categories":
        st.subheader("🔍 Filter Students")

    # 🔥 FIX MERGE ERROR (important)
        df["Student ID"] = df["Student ID"].astype(str).str.strip()
        model_data["Student_ID"] = model_data["Student_ID"].astype(str).str.strip()

    # 📅 Admission Year Filter
        if "Admission Year" in df.columns:
            df["Admission Year"] = df["Admission Year"].astype(str)
            year_filter = st.selectbox(
                "Select Admission Year",
                ["All"] + sorted(df["Admission Year"].dropna().unique().tolist())
            )
        else:
            year_filter = "All"

    # -----------------------------
    # MERGE
    # -----------------------------
        filtered_df = model_data.merge(
            df,
            left_on="Student_ID",
            right_on="Student ID",
            how="left"
        )

    # -----------------------------
    # APPLY FILTER
    # -----------------------------
        if year_filter != "All":
            filtered_df = filtered_df[
                filtered_df["Admission Year"] == year_filter
            ]

        st.dataframe(filtered_df[
            ["Student_ID", "Academic_Level", "Skill_Level", "Growth_Level", "Performance"]
        ])

        risk_students = filtered_df[filtered_df["Performance"] == "Risk"].copy()

        if "Email" in df.columns:

            df["Student ID"] = df["Student ID"].astype(str).str.strip()
            df["Email"] = df["Email"].astype(str).str.strip().str.lower()

            risk_students = risk_students.merge(
                df[["Student ID", "Email"]],
                left_on="Student_ID",
                right_on="Student ID",
                how="left"
            )

        st.markdown("## 🔴 Risk Students")

        if not risk_students.empty:


            report_data=convert_to_readable(risk_students)
            report_data = report_data.reset_index(drop=True)
            report_data = report_data.loc[:, ~report_data.columns.duplicated()]
            report_data = report_data.drop_duplicates(subset=["Student_ID"])
            st.dataframe(report_data)

            if st.button("📧 Send Email Alerts"):

                success = 0
                failed = 0

                for _, row in risk_students.iterrows():

                    email = str(row.get("Email")).strip()

                    if email and email != "nan":

                        result = send_email(email, row["Student_ID"])

                        if result is True:
                            success += 1
                        else:
                            failed += 1
                            st.error(f"{email} → {result}")

                st.success(f"✅ Emails Sent: {success}")
                st.warning(f"❌ Failed: {failed}")

        else:
            st.success("No Risk Students")

    # -----------------------------
    # ANALYSIS
    # -----------------------------
    if selected_tab == "Analysis":

        X = model_data[["CGPA","Attendance","Backlogs","Total_Marks","Internships","Activity_Score"]]
        y = model_data["Performance"]

        if len(y.unique()) < 2:
            st.error("❌ Need multiple categories")
            st.stop()

    
        X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
            X, y, model_data["Student_ID"],
            test_size=0.2,
            random_state=42,
            stratify=y
)
        scaler = StandardScaler()

        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        lr = LogisticRegression(max_iter=2000)
        dt = DecisionTreeClassifier()
        rf = RandomForestClassifier()

        lr.fit(X_train_s, y_train)
        dt.fit(X_train, y_train)
        rf.fit(X_train, y_train)
        rf_pred = rf.predict(X_test)

        acc_df = pd.DataFrame({
            "Model": ["Logistic","Decision Tree","Random Forest"],
            "Accuracy": [
                accuracy_score(y_test, lr.predict(X_test_s)),
                accuracy_score(y_test, dt.predict(X_test)),
                accuracy_score(y_test, rf.predict(X_test))
            ]
        })

        st.dataframe(acc_df)
        st.bar_chart(acc_df.set_index("Model"))

        labels = sorted(y.unique())

        cm = confusion_matrix(y_test, rf_pred, labels=labels)

        fig, ax = plt.subplots(figsize=(4,3))

        sns.heatmap(cm, annot=True, fmt="d",
                    xticklabels=labels,
                    yticklabels=labels,
                    annot_kws={"size":10},
                    ax=ax)

        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")

        st.pyplot(fig)
        # ❌ WRONG PREDICTIONS
        results = pd.DataFrame({
            "Student_ID": ids_test,
            "Actual": y_test,
            "Predicted": rf_pred
        })

        wrong_predictions = results[results["Actual"] != results["Predicted"]]

        st.subheader("❌ Wrong Predictions")
        st.dataframe(wrong_predictions)

    # -----------------------------
    # FINAL REPORT
    # -----------------------------
    if selected_tab == "Final Report":

        model_data["Suggestion"] = model_data["Performance"].apply(
            lambda x: "Improve Immediately" if x == "Risk" else "Maintain"
        )
        model_data.to_csv("final_report.csv", index=False)

        st.success("✅ Final report saved successfully!")
        report_data = convert_to_readable(model_data)
        st.dataframe(report_data)

        st.download_button(
            "Download Report",
            model_data.to_csv(index=False),
            "final_report.csv"
        )
          # -----------------------------
# GRIEVANCE VIEW (ADMIN)
# -----------------------------
    
    if selected_tab == "Grievance":
        st.title("📩 Student Grievances")

        grievance_file = "grievance.csv"

        if os.path.exists(grievance_file):
            grievance_df = pd.read_csv(grievance_file)

            if grievance_df.empty:
                st.info("No grievances submitted yet")
            else:
                st.dataframe(grievance_df)

        else:
            st.warning("No grievance file found")  

    # -----------------------------
    # LOGOUT
    # -----------------------------
    if selected_tab == "Logout":
        st.session_state["admin_logged_in"] = False
        st.rerun()
    