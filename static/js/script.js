document.addEventListener('DOMContentLoaded', () => {
    
    // Elements
    const generateBtn = document.getElementById('generate-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('section');

    const loadingMessages = [
        "Crafting cinematic vision...",
        "Writing emotional dialogue...",
        "Designing soundscape...",
        "Planning cinematography...",
        "Finalizing script..."
    ];

    // State
    let messageInterval;

    // --- Navigation ---
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.classList.contains('disabled')) return;
            
            // Remove active class from all buttons
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Show target section
            const targetId = btn.getAttribute('data-target');
            sections.forEach(sec => sec.classList.remove('active-section'));
            document.getElementById(targetId).classList.add('active-section');
        });
    });

    // --- Generation Logic ---

    generateBtn.addEventListener('click', async () => {
        const story = document.getElementById('story-input').value;
        const genre = document.getElementById('genre-select').value;

        if (!story) {
            alert("Please enter a story concept.");
            return;
        }

        startLoading();

        try {
            // 1. Generate Screenplay
            const response = await fetch('/generate_screenplay', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ story, genre })
            });
            const data = await response.json();
            
            document.getElementById('screenplay-content').textContent = data.content;
            document.getElementById('display-genre').textContent = genre.toUpperCase();

            // Enable Sidebar
            document.getElementById('nav-screenplay').classList.remove('disabled');
            document.getElementById('nav-characters').classList.remove('disabled'); // Enable next likely step

            stopLoading();
            
            // Auto-switch to screenplay view
            document.getElementById('nav-screenplay').click();

        } catch (error) {
            console.error(error);
            alert("An error occurred during generation.");
            stopLoading();
        }
    });

    // --- Helper for chained generation ---
    window.generateNext = async (type) => {
        startLoading();
        
        let endpoint = '';
        let targetId = '';
        let navId = '';

        if (type === 'characters') {
            endpoint = '/generate_characters';
            targetId = 'characters-content';
            navId = 'nav-characters';
        } else if (type === 'director_mode') {
            endpoint = '/generate_director_mode';
            targetId = 'director-content';
            navId = 'nav-director';
        } else if (type === 'sound_design') {
            endpoint = '/generate_sound_design';
            targetId = 'sound-content';
            navId = 'nav-sound';
        } else if (type === 'pitch_deck') {
            endpoint = '/generate_pitch_deck';
            targetId = 'pitch-content';
            navId = 'nav-pitch';
        }

        try {
            const response = await fetch(endpoint, { method: 'POST' });
            const data = await response.json();
            
            if (data.error) {
                alert(data.error);
                stopLoading();
                return;
            }

            document.getElementById(targetId).textContent = data.content;
            
            // Unlock nav
            const navBtn = document.getElementById(navId);
            navBtn.classList.remove('disabled');
            navBtn.click(); // Auto-navigate

        } catch (error) {
            console.error(error);
            alert("Error generating content.");
        } finally {
            stopLoading();
        }
    };


    // --- Loading Animation ---
    function startLoading() {
        loadingOverlay.classList.remove('hidden');
        let i = 0;
        messageInterval = setInterval(() => {
            loadingText.textContent = loadingMessages[i % loadingMessages.length];
            i++;
        }, 1500);
    }

    function stopLoading() {
        loadingOverlay.classList.add('hidden');
        clearInterval(messageInterval);
    }

});
