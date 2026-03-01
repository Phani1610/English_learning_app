"""
English Learning Web App - Flask Backend
Features:
- Speech to Text
- Text to Speech
- Grammar Checker
- Grammar Quiz API
- AI Chatbot (Ollama)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import tempfile
import os
from gtts import gTTS


# Set NLTK data path before importing textblob
import nltk
nltk.data.path.append(os.path.expanduser('~\\AppData\\Roaming\\nltk_data'))

# Speech Recognition & TTS
import speech_recognition as sr
import pyttsx3

# Grammar Checker
from textblob import TextBlob

# Ollama for AI Chatbot
import requests

app = Flask(__name__)
CORS(app)

# Initialize speech recognition
recognizer = sr.Recognizer()

# Initialize TTS engine
tts_engine = pyttsx3.init()

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
  # You can use any model you have installed
OLLAMA_MODEL = "llava-llama3:8b"  # User's installed model

# Grammar Quiz Questions Database
GRAMMAR_QUIZ = [
    {
        "id": 1,
        "question": "Which sentence is correct?",
        "options": [
            "She don't like apples.",
            "She doesn't like apples.",
            "She not like apples.",
            "She no like apples."
        ],
        "correct_answer": 1,
        "explanation": "'Doesn't' is the correct contraction for 'does not' with third person singular."
    },
    {
        "id": 2,
        "question": "Choose the correct past tense:",
        "options": [
            "I have went to school.",
            "I have gone to school.",
            "I go to school yesterday.",
            "I went to school."
        ],
        "correct_answer": 1,
        "explanation": "'Gone' is the past participle used with 'have/has'."
    },
    {
        "id": 3,
        "question": "Which is the correct plural form?",
        "options": [
            "Childs",
            "Childrens",
            "Children",
            "Childes"
        ],
        "correct_answer": 2,
        "explanation": "'Children' is the correct irregular plural of 'child'."
    },
    {
        "id": 4,
        "question": "Select the correct comparative form:",
        "options": [
            "She is more smarter than him.",
            "She is smarter than him.",
            "She is more smart than him.",
            "She is smart than him."
        ],
        "correct_answer": 1,
        "explanation": "'Smarter' is the correct comparative form of 'smart' (one-syllable adjective)."
    },
    {
        "id": 5,
        "question": "Which sentence uses the correct article?",
        "options": [
            "I need an unique idea.",
            "I need a unique idea.",
            "I need the unique idea.",
            "I need some unique idea."
        ],
        "correct_answer": 1,
        "explanation": "'A' is used before consonant sounds, 'an' before vowel sounds. 'Unique' starts with a 'yoo' consonant sound."
    }
]

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "message": "English Learning App API is running",
        "endpoints": [
            "POST /speech-to-text",
            "POST /text-to-speech",
            "POST /check-grammar",
            "GET /quiz",
            "POST /chatbot"
        ]
    })


# ==================== SPEECH TO TEXT ====================

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    """
    Convert audio to text using SpeechRecognition
    
    Request JSON:
    {
        "audio_data": "<base64 encoded audio>"  // Optional: for file upload
        OR
        "language": "en-US"  // Language code (default: en-US)
    }
    
    Returns:
    {
        "success": true/false,
        "text": "recognized text",
        "error": "error message if any"
    }
    """
    try:
        data = request.get_json() or {}
        language = data.get('language', 'en-US')
        
        # Use microphone for speech recognition
        with sr.Microphone() as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Listen for audio
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Recognize speech
            text = recognizer.recognize_google(audio, language=language)
            
            return jsonify({
                "success": True,
                "text": text,
                "language": language
            })
            
    except sr.UnknownValueError:
        return jsonify({
            "success": False,
            "text": None,
            "error": "Speech not understood. Please try again."
        }), 400
        
    except sr.RequestError as e:
        return jsonify({
            "success": False,
            "text": None,
            "error": f"Speech recognition service error: {str(e)}"
        }), 503
        
    except Exception as e:
        return jsonify({
            "success": False,
            "text": None,
            "error": f"Error: {str(e)}"
        }), 500


# ==================== TEXT TO SPEECH ====================

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech using gTTS (Render compatible)
    """
    try:
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Text is required"
            }), 400

        text = data['text']
        language = data.get("language", "en")

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_path = temp_file.name
        temp_file.close()

        # Generate speech
        tts = gTTS(text=text, lang=language)
        tts.save(temp_path)

        # Return audio file directly
        return send_file(
            temp_path,
            mimetype="audio/mpeg",
            as_attachment=False
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error converting text to speech: {str(e)}"
        }), 500

# ==================== GRAMMAR CHECKER ====================

@app.route('/check-grammar', methods=['POST'])
def check_grammar():
    """
    Check grammar using TextBlob
    
    Request JSON:
    {
        "text": "Text to check"
    }
    
    Returns:
    {
        "success": true/false,
        "original_text": "original text",
        "corrected_text": "corrected text",
        "is_correct": true/false,
        "suggestions": [
            {
                "type": "grammar/spelling",
                "offset": position,
                "length": length,
                "suggestion": "correct word",
                "message": "explanation"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Text is required"
            }), 400
        
        text = data['text']
        
        # Create TextBlob object
        blob = TextBlob(text)
        
        # Get corrected text
        corrected_text = str(blob.correct())
        
        # Check if text is correct
        is_correct = (text.strip() == corrected_text.strip())
        
        # Generate suggestions
        suggestions = []
        
        # Check each word for spelling/grammar issues
        for word in blob.words:
            # Check if word might be misspelled
            word_lower = word.string.lower()
            if word_lower != word.string.lower():
                suggestions.append({
                    "type": "spelling",
                    "offset": word.position,
                    "length": len(word.string),
                    "suggestion": word.string.lower(),
                    "message": f"Possible spelling error: '{word.string}'"
                })
        
        # Check for common grammar issues using parse tree
        for sentence in blob.sentences:
            # Check sentence structure
            if sentence.tags:
                # Look for common errors
                for i in range(len(sentence.tags) - 1):
                    # Check for double negatives
                    if sentence.tags[i][1] == 'DT' and sentence.tags[i+1][1] == 'DT':
                        continue
        
        return jsonify({
            "success": True,
            "original_text": text,
            "corrected_text": corrected_text,
            "is_correct": is_correct,
            "suggestions": suggestions,
            "word_count": len(blob.words),
            "sentence_count": len(blob.sentences)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error checking grammar: {str(e)}"
        }), 500


# ==================== GRAMMAR QUIZ ====================

@app.route('/quiz', methods=['GET'])
def get_quiz():
    """
    Get 5 random grammar MCQ questions
    
    Returns:
    {
        "success": true/false,
        "questions": [
            {
                "id": 1,
                "question": "question text",
                "options": ["option1", "option2", ...],
                "correct_answer": index
            }
        ]
    }
    """
    try:
        # Shuffle and return 5 questions
        import random
        questions = random.sample(GRAMMAR_QUIZ, min(5, len(GRAMMAR_QUIZ)))
        
        # Return questions (without correct answer for quiz)
        quiz_questions = []
        for q in questions:
            quiz_questions.append({
                "id": q["id"],
                "question": q["question"],
                "options": q["options"]
                # Note: correct_answer is intentionally omitted for quiz
            })
        
        return jsonify({
            "success": True,
            "questions": quiz_questions,
            "total_questions": len(GRAMMAR_QUIZ)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error fetching quiz: {str(e)}"
        }), 500


@app.route('/quiz/verify', methods=['POST'])
def verify_quiz_answer():
    """
    Verify quiz answer
    
    Request JSON:
    {
        "question_id": 1,
        "answer": 1  // selected option index
    }
    
    Returns:
    {
        "success": true/false,
        "correct": true/false,
        "explanation": "explanation text"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'question_id' not in data or 'answer' not in data:
            return jsonify({
                "success": False,
                "error": "question_id and answer are required"
            }), 400
        
        question_id = data['question_id']
        answer = data['answer']
        
        # Find the question
        question = next((q for q in GRAMMAR_QUIZ if q['id'] == question_id), None)
        
        if not question:
            return jsonify({
                "success": False,
                "error": "Question not found"
            }), 404
        
        is_correct = (answer == question['correct_answer'])
        
        return jsonify({
            "success": True,
            "correct": is_correct,
            "correct_answer": question['correct_answer'],
            "explanation": question['explanation']
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error verifying answer: {str(e)}"
        }), 500


# ==================== AI CHATBOT ====================

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """
    AI Chatbot using Ollama for English grammar assistance
    
    Request JSON:
    {
        "message": "User message",
        "history": [
            {"role": "user", "content": "previous message"},
            {"role": "assistant", "content": "previous response"}
        ]
    }
    
    Returns:
    {
        "success": true/false,
        "response": "AI response",
        "error": "error message if any"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        user_message = data['message']
        history = data.get('history', [])
        
        # Build system prompt for English grammar assistant
        system_prompt = """You are an English Grammar Assistant chatbot. Your role is to help users with:
1. Grammar explanations and corrections
2. Spelling and punctuation help
3. Sentence structure improvements
4. Word usage and vocabulary
5. General English learning questions

Always be:
- Clear and concise in explanations
- Patient and encouraging
- Provide examples when helpful
- Explain the reasoning behind corrections

If a user asks about topics unrelated to English grammar or learning, politely redirect them to English-related questions."""
        
        # Build messages for Ollama
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        for msg in history[-5:]:  # Last 5 messages
            messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        # Call Ollama API
        payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('message', {}).get('content', 'No response from AI')
            
            return jsonify({
                "success": True,
                "response": ai_response,
                "message": user_message
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Ollama API error: {response.status_code}"
            }), 503
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "error": "Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434"
        }), 503
        
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "AI request timed out. Please try again."
        }), 504
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Chatbot error: {str(e)}"
        }), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 50)
    print("English Learning App - Flask Backend")
    print("=" * 50)
    print("Starting server on http://127.0.0.1:5000")
    print("\nAvailable Endpoints:")
    print("  POST /speech-to-text  - Convert speech to text")
    print("  POST /text-to-speech  - Convert text to speech")
    print("  POST /check-grammar   - Check grammar")
    print("  GET  /quiz            - Get grammar quiz")
    print("  POST /chatbot         - AI Chatbot")
    print("=" * 50)
    
    app.run(debug=True, port=5000)
