// chrome-plugin/popup.js
document.addEventListener('DOMContentLoaded', () => {
    const processVideoBtn = document.getElementById('process-video-btn');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatBox = document.getElementById('chat-box');
    const statusDiv = document.getElementById('status');

    let currentVideoId = null;

    // Get current tab URL to see if it's a YouTube video
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const url = tabs[0].url;
        if (url.includes("youtube.com/watch")) {
            statusDiv.textContent = 'Ready to process this video.';
        } else {
            statusDiv.textContent = 'Navigate to a YouTube video to use this extension.';
            processVideoBtn.disabled = true;
        }
    });

    processVideoBtn.addEventListener('click', () => {
        statusDiv.textContent = 'Processing video...';
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const url = tabs[0].url;
            fetch('http://127.0.0.1:5000/process_video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ youtube_url: url })
            })
            .then(response => response.json())
            .then(data => {
                if (data.video_id) {
                    currentVideoId = data.video_id;
                    statusDiv.textContent = 'Video processed! You can now ask questions.';
                    userInput.disabled = false;
                    sendBtn.disabled = false;
                    processVideoBtn.disabled = true;
                } else {
                    statusDiv.textContent = `Error: ${data.error}`;
                }
            })
            .catch(err => statusDiv.textContent = 'Error processing video.');
        });
    });

    sendBtn.addEventListener('click', () => {
        const question = userInput.value;
        if (!question || !currentVideoId) return;

        addMessage(question, 'user');
        userInput.value = '';
        statusDiv.textContent = 'Thinking...';

        fetch('http://127.0.0.1:5000/ask_question', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_id: currentVideoId, question: question })
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.answer, 'bot');
            statusDiv.textContent = 'Ready for your next question.';
        })
        .catch(err => statusDiv.textContent = 'Error getting answer.');
    });

    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = sender === 'user' ? 'user-msg' : 'bot-msg';
        msgDiv.textContent = text;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});