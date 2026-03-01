// English Learning Web App - JavaScript

// API Base URL
const API_BASE = 'http://localhost:5000';

// State Management
const state = {
    currentSection: 'home',
    quizScore: 0,
    currentQuestion: 0,
    selectedAnswer: null,
    quizQuestions: [],
    isRecording: false,
    mediaRecorder: null,
    audioChunks: [],
    chatHistory: []
};

// DOM Elements
const navItems = document.querySelectorAll('.nav-item');
const contentSections = document.querySelectorAll('.content-section');
const cards = document.querySelectorAll('.card');

// Navigation Handling
navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const targetSection = item.getAttribute('data-section');
        navigateToSection(targetSection);
    });
});

cards.forEach(card => {
    card.addEventListener('click', () => {
        const targetSection = card.getAttribute('data-target');
        navigateToSection(targetSection);
    });
});

function navigateToSection(sectionId) {
    // Update nav items
    navItems.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-section') === sectionId) {
            item.classList.add('active');
        }
    });

    // Update content sections
    contentSections.forEach(section => {
        section.classList.remove('active');
        if (section.id === sectionId) {
            section.classList.add('active');
        }
    });

    state.currentSection = sectionId;

    // Load quiz if navigating to quiz section
    if (sectionId === 'quiz' && state.quizQuestions.length === 0) {
        loadQuiz();
    }
}

// Audio to Text - Microphone Functionality
const micBtn = document.getElementById('mic-btn');
const audioResult = document.getElementById('audio-result');

if (micBtn) {
    micBtn.addEventListener('click', async () => {
        if (!state.isRecording) {
            await startRecording();
        } else {
            await stopRecording();
        }
    });
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        state.mediaRecorder = new MediaRecorder(stream);
        state.audioChunks = [];

        state.mediaRecorder.ondataavailable = (event) => {
            state.audioChunks.push(event.data);
        };

        state.mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(state.audioChunks, { type: 'audio/wav' });
            await sendAudioToBackend(audioBlob);
        };

        state.mediaRecorder.start();
        state.isRecording = true;
        micBtn.classList.add('recording');
        micBtn.innerHTML = '<span class="btn-icon">⏹️</span><span>Stop Recording</span>';
    } catch (error) {
        console.error('Error starting recording:', error);
        showNotification('Error accessing microphone. Please check permissions.', 'error');
    }
}

async function stopRecording() {
    if (state.mediaRecorder && state.isRecording) {
        state.mediaRecorder.stop();
        state.isRecording = false;
        micBtn.classList.remove('recording');
        micBtn.innerHTML = '<span class="btn-icon">🎤</span><span>Start Recording</span>';
        
        // Stop all tracks
        state.mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
}

async function sendAudioToBackend(audioBlob) {
    showLoading(audioResult, 'Processing audio...');
    
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');

    try {
        const response = await fetch(`${API_BASE}/speech-to-text`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (data.success) {
            audioResult.value = data.text;
            showNotification('Audio converted to text successfully!', 'success');
        } else {
            audioResult.value = '';
            showNotification(data.error || 'Failed to convert audio to text', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        audioResult.value = '';
        showNotification('Failed to connect to server', 'error');
    }
    
    hideLoading(audioResult);
}

// Text to Speech
const speakBtn = document.getElementById('speak-btn');
const ttsInput = document.getElementById('tts-input');

if (speakBtn) {
    speakBtn.addEventListener('click', async () => {
        const text = ttsInput.value.trim();
        
        if (!text) {
            showNotification('Please enter text to speak', 'error');
            return;
        }

        showLoading(speakBtn, 'Speaking...');

        try {
            const response = await fetch(`${API_BASE}/text-to-speech`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            const data = await response.json();

            if (data.success) {
                // Play the audio
                const audio = new Audio(`data:audio/wav;base64,${data.audio}`);
                audio.play();
                showNotification('Text converted to speech!', 'success');
            } else {
                showNotification(data.error || 'Failed to convert text to speech', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Failed to connect to server', 'error');
        }

        hideLoading(speakBtn);
    });
}

// Grammar Checker
const checkGrammarBtn = document.getElementById('check-grammar-btn');
const grammarInput = document.getElementById('grammar-input');
const grammarResult = document.getElementById('grammar-result');

if (checkGrammarBtn) {
    checkGrammarBtn.addEventListener('click', async () => {
        const text = grammarInput.value.trim();
        
        if (!text) {
            showNotification('Please enter text to check grammar', 'error');
            return;
        }

        showLoading(checkGrammarBtn, 'Checking...');

        try {
            const response = await fetch(`${API_BASE}/check-grammar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            const data = await response.json();

            if (data.success) {
                // Format suggestions properly
                let suggestionsHtml = '';
                if (data.suggestions && data.suggestions.length > 0) {
                    suggestionsHtml = '<ul class="suggestions-list">';
                    data.suggestions.forEach(suggestion => {
                        suggestionsHtml += `<li>${suggestion.message}</li>`;
                    });
                    suggestionsHtml += '</ul>';
                }
                
                grammarResult.innerHTML = `
                    <p><strong>Original:</strong> ${text}</p>
                    <p><strong>Corrected:</strong> ${data.corrected_text}</p>
                    ${data.is_correct ? '<p class="correct-text">✓ Your text is grammatically correct!</p>' : '<p class="incorrect-text">✗ Some corrections were made to your text.</p>'}
                    ${suggestionsHtml}
                    <p class="stats"><em>Words: ${data.word_count}, Sentences: ${data.sentence_count}</em></p>
                `;
                grammarResult.classList.add('success');
                grammarResult.classList.remove('error');
                showNotification('Grammar checked successfully!', 'success');
            } else {
                grammarResult.innerHTML = `<p>${data.error || 'Failed to check grammar'}</p>`;
                grammarResult.classList.add('error');
                grammarResult.classList.remove('success');
                showNotification('Failed to check grammar', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            grammarResult.innerHTML = `<p>Failed to connect to server</p>`;
            grammarResult.classList.add('error');
            showNotification('Failed to connect to server', 'error');
        }

        hideLoading(checkGrammarBtn);
    });
}

// Quiz Functionality
const quizQuestion = document.getElementById('quiz-question');
const quizOptions = document.getElementById('quiz-options');
const quizProgress = document.getElementById('quiz-progress');
const quizScore = document.getElementById('quiz-score');
const nextQuestionBtn = document.getElementById('next-question-btn');
const restartQuizBtn = document.getElementById('restart-quiz-btn');
const quizResult = document.getElementById('quiz-result');

async function loadQuiz() {
    try {
        const response = await fetch(`${API_BASE}/quiz`);
        const data = await response.json();

        if (data.success) {
            state.quizQuestions = data.questions;
            state.currentQuestion = 0;
            state.quizScore = 0;
            displayQuestion();
        } else {
            showNotification('Failed to load quiz questions', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to connect to server', 'error');
    }
}

function displayQuestion() {
    if (state.currentQuestion >= state.quizQuestions.length) {
        showQuizResult();
        return;
    }

    const question = state.quizQuestions[state.currentQuestion];
    
    document.getElementById('question-text').textContent = question.question;
    quizProgress.textContent = `Question ${state.currentQuestion + 1} of ${state.quizQuestions.length}`;
    quizScore.textContent = `Score: ${state.quizScore}`;
    
    // Clear previous options
    quizOptions.innerHTML = '';
    state.selectedAnswer = null;
    nextQuestionBtn.disabled = true;

    // Create option buttons
    question.options.forEach((option, index) => {
        const button = document.createElement('button');
        button.className = 'quiz-option';
        button.textContent = option;
        button.addEventListener('click', () => selectAnswer(index, question.correctAnswer));
        quizOptions.appendChild(button);
    });

    quizResult.style.display = 'none';
}

function selectAnswer(selectedIndex, correctIndex) {
    const options = quizOptions.querySelectorAll('.quiz-option');
    
    // Disable all options
    options.forEach((option, index) => {
        option.disabled = true;
        
        if (index === correctIndex) {
            option.classList.add('correct');
        }
    });

    // Mark selected answer
    if (selectedIndex !== correctIndex) {
        options[selectedIndex].classList.add('incorrect');
    } else {
        state.quizScore++;
    }

    state.selectedAnswer = selectedIndex;
    quizScore.textContent = `Score: ${state.quizScore}`;
    nextQuestionBtn.disabled = false;
}

if (nextQuestionBtn) {
    nextQuestionBtn.addEventListener('click', () => {
        state.currentQuestion++;
        displayQuestion();
    });
}

if (restartQuizBtn) {
    restartQuizBtn.addEventListener('click', () => {
        state.currentQuestion = 0;
        state.quizScore = 0;
        displayQuestion();
    });
}

function showQuizResult() {
    quizQuestion.style.display = 'none';
    quizOptions.style.display = 'none';
    document.querySelector('.quiz-actions').style.display = 'none';
    quizResult.style.display = 'block';
    
    document.getElementById('final-score').textContent = 
        `You scored ${state.quizScore} out of ${state.quizQuestions.length}`;
    
    showNotification(`Quiz complete! Score: ${state.quizScore}/${state.quizQuestions.length}`, 'success');
}

// Chatbot Functionality
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const chatMessages = document.getElementById('chat-messages');

if (sendBtn) {
    sendBtn.addEventListener('click', sendMessage);
}

if (chatInput) {
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

async function sendMessage() {
    const message = chatInput.value.trim();
    
    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    
    // Add to history
    state.chatHistory.push({ role: 'user', content: message });
    
    chatInput.value = '';

    // Show loading indicator
    const loadingMessage = document.createElement('div');
    loadingMessage.className = 'message bot-message loading-message';
    loadingMessage.innerHTML = '<span class="loading"></span> Thinking...';
    chatMessages.appendChild(loadingMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch(`${API_BASE}/chatbot`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                message: message,
                history: state.chatHistory
            })
        });

        const data = await response.json();

        // Remove loading message
        loadingMessage.remove();

        if (data.success) {
            addMessage(data.response, 'bot');
            // Add bot response to history
            state.chatHistory.push({ role: 'assistant', content: data.response });
        } else {
            // Display actual error message from backend
            const errorMsg = data.error || 'Sorry, I encountered an error. Please try again.';
            addMessage(errorMsg, 'bot');
            showNotification(errorMsg, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        loadingMessage.remove();
        const errorMsg = 'Failed to connect to server. Please check if the backend is running.';
        addMessage(errorMsg, 'bot');
        showNotification(errorMsg, 'error');
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.innerHTML = `<p>${text}</p>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Utility Functions
function showLoading(element, text) {
    if (element.tagName === 'TEXTAREA') {
        element.value = '';
        element.placeholder = text;
    } else {
        element.dataset.originalText = element.innerHTML;
        element.innerHTML = `<span class="loading"></span> ${text}`;
        element.disabled = true;
    }
}

function hideLoading(element) {
    if (element.tagName === 'TEXTAREA') {
        element.placeholder = element.id === 'audio-result' ? 
            'Your speech will appear here...' : 
            'Enter text to speak...';
    } else {
        element.innerHTML = element.dataset.originalText;
        element.disabled = false;
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 10px;
        background: ${type === 'success' ? 'rgba(0, 230, 118, 0.9)' : 'rgba(255, 82, 82, 0.9)'};
        color: white;
        font-weight: 600;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('English Learning App initialized');
    navigateToSection('home');
});
