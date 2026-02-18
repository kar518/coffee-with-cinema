import os
import json
import logging
import requests
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_session import Session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document
import io

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Flask-Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "granite-code:3b"  # Or another model available locally

def query_ollama(prompt, system_prompt=""):
    """
    Helper function to query the local Ollama instance.
    """
    full_prompt = f"{system_prompt}\n\n{prompt}"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 2048
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama connection error: {e}")
        return None  # Return None to indicate failure/fallback

# --- Mock Data Generation (Fallback) ---
def mock_screenplay(story, genre):
    return f"""INT. OFFICE - DAY

A dimly lit room. DETECTIVE MILLER sits behind a desk, nursing a glass of whiskey. Rain hammers against the window.

MILLER
(V.O.)
They say time heals all wounds. But in this city, time just festers.

He looks at the photo of a missing girl on his desk.

MILLER
I'm coming for you, kid.

This is a MOCK screenplay for the story: "{story}" in the genre "{genre}". 
Please ensure Ollama is running for real AI generation."""

def mock_characters(story):
    return """**Detective Miller**
Age: 45
Motivation: Redemption for a past failure.
Flaw: Alcoholism and cynicism.

**The antagonist**
Age: Unknown
Motivation: Chaos.
"""

def mock_director_mode(screenplay):
    return """**Scene 1**
Camera: Low angle, tracking shot via the window.
Lighting: Low-key, noir style with heavy shadows.
Color: Desaturated blue cold tones.
"""

def mock_pitch_deck(story):
    return f"""**Title:** The Last Case
**Logline:** A burnt-out detective must face his demons to save a missing girl.
**Target Audience:** 18-35, fans of Neo-Noir.
**Comparable Films:** Se7en, Blade Runner.
"""

def mock_sound_design(screenplay):
    return """**Scene 1**
Music: Slow, melancholic jazz saxophone.
SFX: Heavy rain, distant sirens, glass clinking.
"""

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_screenplay', methods=['POST'])
def generate_screenplay():
    data = request.json
    story = data.get('story')
    genre = data.get('genre')
    
    system_prompt = f"You are a professional Hollywood screenwriter. Write a screenplay in {genre.upper()} cinematic style. Use proper screenplay format: Scene headings in ALL CAPS, Character names centered, Emotional depth, Strong pacing. Visual storytelling."
    prompt = f"Story idea: {story}"
    
    response = query_ollama(prompt, system_prompt)
    if not response:
        response = mock_screenplay(story, genre)
        
    session['screenplay'] = response
    session['story'] = story # Store story for other generators
    session['genre'] = genre
    
    return jsonify({"content": response})

@app.route('/generate_characters', methods=['POST'])
def generate_characters():
    story = session.get('story', '')
    if not story:
        return jsonify({"error": "No story found in session"}), 400
        
    system_prompt = "You are an expert character psychologist. Create deep psychological character profiles. Include Age, Background, Motivation, Internal conflict, Fear, Moral flaw."
    prompt = f"Based on this story idea: {story}"
    
    response = query_ollama(prompt, system_prompt)
    if not response:
        response = mock_characters(story)

    session['characters'] = response
    return jsonify({"content": response})

@app.route('/generate_director_mode', methods=['POST'])
def generate_director_mode():
    screenplay = session.get('screenplay', '')
    if not screenplay:
        return jsonify({"error": "No screenplay found in session"}), 400
        
    system_prompt = "You are a world-class Film Director and Cinematographer. Analyze the screenplay and create a director's shot breakdown. For each scene provide: Camera angle, Shot type, Lighting style, Color grading, Emotional tone."
    prompt = f"Screenplay: {screenplay}"
    
    response = query_ollama(prompt, system_prompt)
    if not response:
        response = mock_director_mode(screenplay)
        
    session['director_mode'] = response
    return jsonify({"content": response})

@app.route('/generate_pitch_deck', methods=['POST'])
def generate_pitch_deck():
    story = session.get('story', '')
    if not story:
        return jsonify({"error": "No story found in session"}), 400
        
    system_prompt = "You are a Hollywood Producer. Create a professional movie pitch document. Include: Logline, Tagline, Genre, Target audience, Comparable films, Why this film will succeed."
    prompt = f"Story idea: {story}"
    
    response = query_ollama(prompt, system_prompt)
    if not response:
        response = mock_pitch_deck(story)
        
    session['pitch_deck'] = response
    return jsonify({"content": response})

@app.route('/generate_sound_design', methods=['POST'])
def generate_sound_design():
    screenplay = session.get('screenplay', '')
    if not screenplay:
        return jsonify({"error": "No screenplay found in session"}), 400

    system_prompt = "You are a professional Sound Designer. Create a sound design plan for the screenplay. Include: Background music genre, Ambient layer details, Foley effects, Dialogue treatment."
    prompt = f"Screenplay: {screenplay}"
    
    response = query_ollama(prompt, system_prompt)
    if not response:
        response = mock_sound_design(screenplay)

    session['sound_design'] = response
    return jsonify({"content": response})

@app.route('/export/<format_type>')
def export_file(format_type):
    # Combine all generated content
    content = ""
    if 'screenplay' in session: content += f"SCREENPLAY\n\n{session['screenplay']}\n\n"
    if 'characters' in session: content += f"CHARACTERS\n\n{session['characters']}\n\n"
    if 'director_mode' in session: content += f"DIRECTOR'S NOTES\n\n{session['director_mode']}\n\n"
    if 'sound_design' in session: content += f"SOUND DESIGN\n\n{session['sound_design']}\n\n"
    if 'pitch_deck' in session: content += f"PITCH DECK\n\n{session['pitch_deck']}\n\n"
    
    if not content:
        return "No content to export", 400

    if format_type == 'pdf':
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        textobject = c.beginText()
        textobject.setTextOrigin(40, 750)
        textobject.setFont("Courier", 12)
        
        for line in content.split('\n'):
            # simple word wrap simulation or just line truncating for MVP
            # A real implementation would handle wrapping better
            if textobject.getY() < 40:
                c.drawText(textobject)
                c.showPage()
                textobject = c.beginText()
                textobject.setTextOrigin(40, 750)
                textobject.setFont("Courier", 12)
            textobject.textLine(line[:90]) # Truncate primarily to avoid crash

        c.drawText(textobject)
        c.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='project_bible.pdf', mimetype='application/pdf')
    
    elif format_type == 'docx':
        doc = Document()
        doc.add_heading('Project Bible', 0)
        doc.add_paragraph(content)
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='project_bible.docx', mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

    return "Invalid format", 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
