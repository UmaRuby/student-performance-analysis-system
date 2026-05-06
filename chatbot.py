from openai import OpenAI
import streamlit as st
import pandas as pd
import time
import os

MODEL = "Meta-Llama-3.3-70B-Instruct"

# -----------------------------
# LOAD LATEST DATASET (🔥 IMPORTANT FIX)
# -----------------------------
def load_dataset():
    csv_exists = os.path.exists("main_dataset.csv")
    excel_exists = os.path.exists("main_dataset.xlsx")

    if not csv_exists and not excel_exists:
        return None

    if csv_exists and excel_exists:
        if os.path.getmtime("main_dataset.xlsx") > os.path.getmtime("main_dataset.csv"):
            return pd.read_excel("main_dataset.xlsx")
        else:
            return pd.read_csv("main_dataset.csv")

    elif excel_exists:
        return pd.read_excel("main_dataset.xlsx")

    else:
        return pd.read_csv("main_dataset.csv")


# -----------------------------
# FIND STUDENT (🔥 FIXED LOGIC)
# -----------------------------
def get_student(df, sid):
    df.columns = df.columns.str.strip()

    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    id_cols = [col for col in df.columns if "id" in col.lower() or "roll" in col.lower()]

    if not id_cols:
        return None, "❌ No ID column found"

    id_col = id_cols[0]

    student = df[df[id_col].str.lower() == sid.strip().lower()]

    if student.empty:
        return None, "❌ Student not found"

    return student.iloc[0].to_dict(), None


# -----------------------------
# SAFE API CALL
# -----------------------------
def safe_api_call(client, prompt, retries=3):
    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful academic assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=80
            )
            return response.choices[0].message.content

        except Exception:
            time.sleep(2 ** i)

    return "⚠️ Too many requests. Try again later."


# -----------------------------
# MAIN CHATBOT FUNCTION (🔥 FIXED)
# -----------------------------
def chatbot_response(student_id, question):
    try:
        df = load_dataset()

        if df is None:
            return "🚫 No dataset available"

        student_info, error = get_student(df, student_id)

        if error:
            return error

        # 🔥 SHORT SMART PROMPT
        prompt = f"""
        You are a smart academic assistant.

        Student Data:
        {student_info}

        Question: {question}

        Answer in MAX 3 lines:
        Answer:
        Reason:
        Suggestion:
        Keep it short and clear.
        """

        client = OpenAI(
            api_key=st.secrets["SAMBANOVA_API_KEY"],
            base_url="https://api.sambanova.ai/v1"
        )

        return safe_api_call(client, prompt)

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# -----------------------------
# CACHE (OPTIONAL SPEED BOOST)
# -----------------------------
@st.cache_data
def get_cached_response(student_id, question):
    return chatbot_response(student_id, question)