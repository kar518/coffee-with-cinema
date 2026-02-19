import streamlit as st
import google.generativeai as genai
import replicate
import os

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

st.set_page_config(page_title="Coffee-with-Cinema", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model_choice_default = "gemini-2.5-flash"

# Replicate client (uses environment variable)
client = replicate.Client()

# ---------------------------------------------------
# IMAGE GENERATION FUNCTION
# ---------------------------------------------------

def generate_image(prompt):
    output = client.run(
        "stability-ai/sdxl",
        input={
            "prompt": prompt,
            "width": 768,
            "height": 512
        }
    )
    return output[0]

# ---------------------------------------------------
# CINEMATIC DARK THEME
# ---------------------------------------------------

st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.block-container {
    padding-top: 2rem;
}
.stButton>button {
    background-color: #E50914;
    color: white;
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "screenplay" not in st.session_state:
    st.session_state.screenplay = ""

if "characters" not in st.session_state:
    st.session_state.characters = ""

if "director" not in st.session_state:
    st.session_state.director = ""

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:
    st.title("⚙ Studio Settings")

    genre = st.selectbox(
        "Genre",
        ["Thriller", "Sci-Fi", "Romance", "Horror", "Noir"]
    )

    tone = st.selectbox(
        "Tone",
        ["Dark", "Inspirational", "Gritty", "Emotional", "Experimental"]
    )

    language = st.selectbox(
        "Language",
        ["English", "Hindi", "Telugu", "Tamil", "Kannada", "Malayalam"]
    )

    model_choice = st.selectbox(
        "Model",
        ["gemini-2.5-flash", "gemini-1.5-pro"],
        index=0
    )

    length = st.slider("Number of Scenes", 1, 6, 3)

model = genai.GenerativeModel(f"models/{model_choice}")

# ---------------------------------------------------
# MAIN UI
# ---------------------------------------------------

st.title("🎬 Coffee-with-Cinema")
st.subheader("AI Cinematic Pre-Production Studio")

st.markdown("---")

story = st.text_area("Enter your story concept", height=150)

col1, col2, col3 = st.columns(3)

with col1:
    generate_script = st.button("🎞 Generate Screenplay")

with col2:
    generate_characters = st.button("🎭 Characters")

with col3:
    generate_director = st.button("🎥 Director Mode")

st.markdown("---")

# ---------------------------------------------------
# GENERATE SCREENPLAY
# ---------------------------------------------------

if generate_script and story:
    prompt = f"""
Write a cinematic screenplay in {genre} style.
Tone: {tone}
Language: {language}
Number of scenes: {length}

Use:
- ALL CAPS scene headings
- Dialogue formatting
- Strong visual storytelling
- Emotional pacing

Story:
{story}
"""
    with st.spinner("Crafting cinematic vision..."):
        response = model.generate_content(prompt)
        st.session_state.screenplay = response.text

# ---------------------------------------------------
# GENERATE CHARACTERS
# ---------------------------------------------------

if generate_characters and st.session_state.screenplay:
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
    with st.spinner("Building character psychology..."):
        response = model.generate_content(char_prompt)
        st.session_state.characters = response.text

# ---------------------------------------------------
# GENERATE DIRECTOR MODE
# ---------------------------------------------------

if generate_director and st.session_state.screenplay:
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
    with st.spinner("Designing cinematic shot plan..."):
        response = model.generate_content(director_prompt)
        st.session_state.director = response.text

# ---------------------------------------------------
# OUTPUT TABS
# ---------------------------------------------------

if st.session_state.screenplay:

    tab1, tab2, tab3 = st.tabs(["🎞 Screenplay", "🎭 Characters", "🎥 Director + Storyboard"])

    # ---------------- SCREENPLAY ----------------
    with tab1:
        st.markdown(st.session_state.screenplay)

        st.download_button(
            label="Download Screenplay",
            data=st.session_state.screenplay,
            file_name="screenplay.txt",
            mime="text/plain"
        )

    # ---------------- CHARACTERS ----------------
    with tab2:
        if st.session_state.characters:
            st.markdown(st.session_state.characters)
        else:
            st.info("Generate character profiles.")

    # ---------------- DIRECTOR + STORYBOARD ----------------
    with tab3:

        if st.session_state.director:

            st.markdown("## 🎬 AI Storyboard")

            # Simple scene split (based on scene headings)
            scenes = st.session_state.screenplay.split("INT.")
            scenes = [s for s in scenes if s.strip() != ""]

            for i, scene in enumerate(scenes):

                st.markdown(f"### Scene {i+1}")

                image_prompt = f"""
Cinematic storyboard frame, film still,
{genre} genre,
{tone} tone,
dramatic lighting,
high detail,
scene description:
{scene[:400]}
"""

                with st.spinner("Generating cinematic frame..."):
                    img_url = generate_image(image_prompt)

                st.image(img_url, use_column_width=True)

                st.markdown("#### 🎥 Director Notes")
                st.markdown(st.session_state.director)
                st.markdown("---")

        else:
            st.info("Generate director breakdown to create storyboard.")