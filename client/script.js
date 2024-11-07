const askButton = document.getElementById('askButton');
const questionInput = document.getElementById('questionInput');
const responseOutput = document.getElementById('responseOutput');
const subtitleBox = document.getElementById('subtitleBox');

async function playAudio(text) {
    try {                    
        const response = await fetch('http://127.0.0.1:4999/get_fortune_audio', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({"text": text})
        });

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        
        const audio = new Audio(audioUrl);
        
        audio.onended = () => {
            setTimeout(() => {
                subtitleBox.style.transition = "opacity 2s";
                subtitleBox.style.opacity = "0";
                setTimeout(() => {
                    subtitleBox.style.display = "none";
                    subtitleBox.style.opacity = "1";
                    subtitleBox.style.transition = "none";
                }, 2000);
            }, 3000);
        };
        
        await audio.play();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function handleQuestion() {
    const question = questionInput.value.trim();
    if (question) {
        // Clear previous response and show loading
        responseOutput.innerText = "The raven is pondering your question...";
        
        try {
            // Step 1: Get text response and audio URL
            const response = await fetch('http://127.0.0.1:4999/get_fortune', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ question })
            });

            const data = await response.json();
            
            // Handle subtitles
            subtitleBox.innerText = data.text;
            responseOutput.innerText = "";
            subtitleBox.style.display = "block";

            await playAudio(data.text);
            
        } catch (error) {
            responseOutput.innerText = "The raven encountered an error...";
            console.error(error);
        }
    }
}

askButton.addEventListener('click', handleQuestion);
questionInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        handleQuestion();
    }
});
