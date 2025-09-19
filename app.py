from flask import Flask, render_template, jsonify, request
import ollama
from dotenv import load_dotenv
from processed_data import get_relevant_content
from special import instructions
from database import db_session
import logging
import random
import json
import os
from typing import List

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Add this constant at the top of the file
## RANDOM_QUESTIONS_FILE = os.path.join('data', 'random_questions.json')
DEFAULT_QUESTIONS_FILE = os.path.join('static', 'default_questions.json')

# Function to generate random questions
def retreive_random_questions() -> List[str]:
    ## The commented out portion retrieves AI generated questions, with default_questions as a fallback.
    # try:
    #     with open(RANDOM_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    #         all_questions = json.load(f)
    #     return random.sample(all_questions, 4)
    # except (FileNotFoundError, json.JSONDecodeError):
    #     with open(DEFAULT_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    #         default_questions = json.load(f)
    #     return random.sample(default_questions, 4)
    with open(DEFAULT_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            default_questions = json.load(f)
    return random.sample(default_questions, 4)

# Route for home page
@app.route('/')
def home():
    random_questions=retreive_random_questions()
    # with open(RANDOM_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    #     random_questions = json.load(f)
    return render_template('home.html', random_questions=random_questions)

# Static page example
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/ask_ollama', methods=['POST'])
def ask_ollama():
    question = request.json.get('question')
    logger.debug(f"Received question: {question}")
    
    if question:
        try:
            logger.debug("Getting relevant content")
            relevant_content = get_relevant_content(question)
            context = "\n".join(relevant_content)
            
            logger.debug("Forming prompt")
            prompt = f"Instructions: {instructions}\n\nContext: {context}\n\nQuestion: {question}"
            
            logger.debug("Generating response with Ollama")
            response = ollama.generate(model="llama3.1:8b", prompt=prompt,
                                       options={
                                           'top_k': 20,
                                           'top_p': .70,
                                           'temperature': .50,
                                           'mirostat': 2.0,
                                           'mirostat_tau': 3.0,
                                           'repeat_penalty': 1.35
                                            }
                                        )
            logger.debug(f"Ollama response: {response}")
            return jsonify({"response": response['response']})
        
        except Exception as e:
            logger.error(f"Error in ask_ollama: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    logger.warning("No question provided")
    return jsonify({"error": "No question provided"}), 400

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5005)
