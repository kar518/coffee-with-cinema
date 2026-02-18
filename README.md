# Coffee-with-Cinema: AI Cinematic Pre-Production Studio

An AI-powered web application that transforms a simple story idea into a complete cinematic pre-production package.

## Features

- **Screenplay Generation**: Creates industry-standard screenplays based on genre and mood.
- **Character Profiles**: Deep psychological analysis of characters.
- **Director Mode**: Detailed shot breakdown, camera angles, and lighting suggestions.
- **Sound Design**: Plan for music, ambient layers, and foley.
- **Pitch Deck**: Investor-ready business proposal generator.
- **Export**: Download your project bible as PDF or DOCX.

## Setup Instructions

1.  **Prerequisites**:
    - Python 3.8+
    - [Ollama](https://ollama.ai/) installed and running (`ollama serve`).
    - Pull the Granite model: `ollama pull granite-code:3b` (or update `MODEL_NAME` in `app.py` to your preferred model).

2.  **Installation**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**:
    ```bash
    python app.py
    ```

4.  **Access cleanly**:
    Open your browser and navigate to `http://localhost:5000`.

## Design Notes

This project uses a cinematic dark mode UI with glassmorphism effects to provide an immersive experience for filmmakers.
The backend is powered by Flask and uses local LLM inference via Ollama for privacy and cost-efficiency.
