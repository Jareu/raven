const askButton = document.getElementById('askButton');
const questionInput = document.getElementById('questionInput');
const responseOutput = document.getElementById('responseOutput');
const subtitleBox = document.getElementById('subtitleBox');

async function playAudioAsync(text) {
    try {                    
        const response = await fetch('/raven_server.php/get_fortune_audio', {
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
        $("#responseOutput").show();
        responseOutput.innerText = "The raven is pondering your question...";
        
        try {
            var respone = await getFortuneAsync(question);

            handleSubtitles(respone);

            await playAudioAsync(respone);
            
        } catch (error) {
            $("#responseOutput").show();
            responseOutput.innerText = "The raven encountered an error...";
            console.error(error);
        }
    }
}

async function getFortuneAsync(question)
{
    const response = await fetch('/raven_server.php/get_fortune', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ question })
    });

    const data = await response.json();

    return data.text;
}

function handleSubtitles(text)
{
    subtitleBox.innerText = text;
    responseOutput.innerText = "";
    $("#responseOutput").hide();
    subtitleBox.style.display = "block";
}

askButton.addEventListener('click', handleQuestion);
questionInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        handleQuestion();
    }
});
