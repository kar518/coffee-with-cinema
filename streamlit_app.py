import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Coffee-with-Cinema", layout="centered")

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "screenplay" not in st.session_state:
    st.session_state.screenplay = ""

# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.title("🎬 Coffee-with-Cinema")
st.subheader("AI Cinematic Studio")

story = st.text_area("Enter your story idea")

col1, col2 = st.columns(2)

with col1:
    genre = st.selectbox(
        "Genre",
        ["Thriller", "Sci-Fi", "Romance", "Horror", "Noir"]
    )

    tone = st.selectbox(
        "Tone",
        ["Dark", "Inspirational", "Gritty", "Emotional", "Experimental"]
    )

with col2:
    language = st.selectbox(
        "Language",
        ["English", "Hindi", "Telugu", "Tamil", "Kannada", "Malayalam"]
    )

    model_choice = st.selectbox(
        "Model",
        ["gemini-2.5-flash", "gemini-1.5-pro"]
    )

length = st.slider("Number of Scenes", 1, 6, 3)

model = genai.GenerativeModel(f"models/{model_choice}")

# ---------------------------------------------------
# SCREENPLAY GENERATION
# ---------------------------------------------------

if st.button("Generate Screenplay"):

    if story:

        prompt = f"""
Write a cinematic screenplay in {genre} style.
Tone: {tone}
Language: {language}
Number of scenes: {length}

Use:
- ALL CAPS scene headings
- Dialogue
- Action descriptions
- Strong emotional pacing

Story:
{story}
"""

        with st.spinner("Crafting cinematic vision..."):
            response = model.generate_content(prompt)

            st.session_state.screenplay = response.text
            st.session_state.history.append(response.text)

    else:
        st.warning("Please enter a story idea.")

# ---------------------------------------------------
# DISPLAY OUTPUT
# ---------------------------------------------------

if st.session_state.screenplay:

    st.markdown("## 🎞 Generated Screenplay")
    st.markdown(st.session_state.screenplay)

    st.download_button(
        label="Download as TXT",
        data=st.session_state.screenplay,
        file_name="screenplay.txt",
        mime="text/plain"
    )

# ---------------------------------------------------
# CHARACTER BREAKDOWN
# ---------------------------------------------------

if st.session_state.screenplay:
    if st.button("Generate Character Profiles"):

        char_prompt = f"""
Analyze the following screenplay and extract main characters.
For each character provide:
- Name
- Age
- Background
- Motivation
- Internal Conflict
- Moral Flaw

Screenplay:
{st.session_state.screenplay}
"""

        with st.spinner("Analyzing characters..."):
            char_response = model.generate_content(char_prompt)
            st.markdown("## 🎭 Character Profiles")
            st.markdown(char_response.text)

# ---------------------------------------------------
# DIRECTOR MODE
# ---------------------------------------------------

if st.session_state.screenplay:
    if st.button("Generate Director Mode"):

        director_prompt = f"""
You are a film director.

Create a shot breakdown for each scene including:
- Camera angle
- Shot type
- Lighting style
- Color grading
- Emotional tone

Screenplay:
{st.session_state.screenplay}
"""

        with st.spinner("Creating director breakdown..."):
            director_response = model.generate_content(director_prompt)
            st.markdown("## 🎥 Director Mode")
            st.markdown(director_response.text)

# ---------------------------------------------------
# HISTORY
# ---------------------------------------------------

if st.session_state.history:
    st.markdown("## 📚 Previous Generations")

    for i, item in enumerate(st.session_state.history[::-1]):
        with st.expander(f"Version {len(st.session_state.history)-i}"):
            st.markdown(item)
