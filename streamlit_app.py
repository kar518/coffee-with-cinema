import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
st.set_page_config(page_title="Coffee-with-Cinema", layout="wide")

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
.stSelectbox, .stTextArea {
    background-color: #1E1E1E;
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
# SIDEBAR CONFIG
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
        ["gemini-2.5-flash", "gemini-1.5-pro"]
    )

    length = st.slider("Number of Scenes", 1, 6, 3)

# Create model after selection
model = genai.GenerativeModel(f"models/{model_choice}")

# ---------------------------------------------------
# MAIN AREA
# ---------------------------------------------------

st.title("🎬 Coffee-with-Cinema")
st.subheader("AI Cinematic Pre-Production Studio")

with st.expander("📖 About Coffee-with-Cinema"):
    st.markdown("""
    **Coffee-with-Cinema** is an AI-powered cinematic pre-production assistant.

    It helps writers and directors transform raw ideas into:
    - Structured screenplays  
    - Character psychology breakdowns  
    - Shot lists and director notes  
    - Sound design plans  
    - Investor-ready pitch decks  

    Powered by Google Gemini, the system augments creative decision-making
    by translating imagination into structured cinematic documentation.

    This tool is designed to accelerate pre-production workflows and
    help creators visualize their story before it reaches production.
    """)


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
# TABS OUTPUT
# ---------------------------------------------------

if st.session_state.screenplay:
    tab1, tab2, tab3 = st.tabs(["🎞 Screenplay", "🎭 Characters", "🎥 Director"])

    with tab1:
        with st.chat_message("assistant"):
            st.markdown(st.session_state.screenplay)

        st.download_button(
            label="Download Screenplay",
            data=st.session_state.screenplay,
            file_name="screenplay.txt",
            mime="text/plain"
        )

    with tab2:
        if st.session_state.characters:
            with st.chat_message("assistant"):
                st.markdown(st.session_state.characters)
        else:
            st.info("Generate character profiles.")

    with tab3:
        if st.session_state.director:
            with st.chat_message("assistant"):
                st.markdown(st.session_state.director)
        else:
            st.info("Generate director breakdown.")