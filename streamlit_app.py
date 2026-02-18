import streamlit as st
import google.generativeai as genai
import os

# Set API Key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("models/gemini-2.5-flash")

st.set_page_config(page_title="Coffee-with-Cinema", layout="centered")

st.title("🎬 Coffee-with-Cinema")
st.subheader("AI Screenplay Generator")

story = st.text_area("Enter your story idea")

genre = st.selectbox(
    "Select Genre",
    ["Thriller", "Sci-Fi", "Romance", "Horror", "Noir"]
)

if st.button("Generate Screenplay"):
    if story:
        prompt = f"""
Write a cinematic screenplay in {genre} style.

Use:
- ALL CAPS scene headings
- Dialogue
- Action descriptions
- Minimum 3 scenes

Story:
{story}
"""
        with st.spinner("Generating screenplay..."):
            response = model.generate_content(prompt)
            st.markdown("## 🎞 Generated Screenplay")
            st.text(response.text)
    else:
        st.warning("Please enter a story idea.")
