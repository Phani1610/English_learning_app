"""
English Learning Web App - Production Ready (Render Compatible)

Features:
- Text to Speech (gTTS)
- Grammar Checker (TextBlob)
- Grammar Quiz
- AI Chatbot (OpenAI API)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
import os
import random
from gtts import gTTS
from textblob import TextBlob
import requests

app = Flask(__name__)
CORS(app)

# ==============================
# CONFIGURATION
# ==============================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

# ==============================
# GRAMMAR QUIZ DATABASE
# ==============================

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
        "explanation": "'Doesn't' is correct for third person singular."
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
        "explanation": "'Children' is the correct irregular plural."
    }
]

# ==============================
# HEALTH CHECK
# ==============================

@app.route('/')
def index():
    return jsonify({
        "status": "running",
        "message": "English Learning API is live on Render 🚀",
        "endpoints": [
            "POST /text-to-speech",
            "POST /check-grammar",
            "GET /quiz",
            "POST /quiz/verify",
            "POST /chatbot"
        ]
    })

# ==============================
# TEXT TO SPEECH
# ==============================

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"success": False, "error": "Text is required"}), 400

        text = data["text"]
        language = data.get("language", "en")

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_path = temp_file.name
        temp_file.close()

        tts = gTTS(text=text, lang=language)
        tts.save(temp_path)

        return send_file(temp_path, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==============================
# GRAMMAR CHECKER
# ==============================

@app.route('/check-grammar', methods=['POST'])
def check_grammar():
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"success": False, "error": "Text is required"}), 400

        text = data["text"]

        blob = TextBlob(text)
        corrected_text = str(blob.correct())
        is_correct = text.strip() == corrected_text.strip()

        return jsonify({
            "success": True,
            "original_text": text,
            "corrected_text": corrected_text,
            "is_correct": is_correct,
            "word_count": len(blob.words),
            "sentence_count": len(blob.sentences)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==============================
# QUIZ
# ==============================

@app.route('/quiz', methods=['GET'])
def get_quiz():
    try:
        questions = random.sample(GRAMMAR_QUIZ, len(GRAMMAR_QUIZ))

        quiz_data = [{
            "id": q["id"],
            "question": q["question"],
            "options": q["options"]
        } for q in questions]

        return jsonify({
            "success": True,
            "questions": quiz_data
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/quiz/verify', methods=['POST'])
def verify_quiz():
    try:
        data = request.get_json()

        if not data or "question_id" not in data or "answer" not in data:
            return jsonify({"success": False, "error": "Invalid request"}), 400

        question = next((q for q in GRAMMAR_QUIZ if q["id"] == data["question_id"]), None)

        if not question:
            return jsonify({"success": False, "error": "Question not found"}), 404

        correct = data["answer"] == question["correct_answer"]

        return jsonify({
            "success": True,
            "correct": correct,
            "correct_answer": question["correct_answer"],
            "explanation": question["explanation"]
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==============================
# AI CHATBOT (OpenAI)
# ==============================

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        if not OPENAI_API_KEY:
            return jsonify({"success": False, "error": "OPENAI_API_KEY not set"}), 500

        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"success": False, "error": "Message is required"}), 400

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful English grammar assistant."},
                {"role": "user", "content": data["message"]}
            ]
        }

        response = requests.post(OPENAI_URL, headers=headers, json=payload)

        result = response.json()
        ai_response = result["choices"][0]["message"]["content"]

        return jsonify({
            "success": True,
            "response": ai_response
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==============================
# MAIN
# ==============================

if __name__ == '__main__':
       port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
