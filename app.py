from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# Carrega as palavras proibidas
def load_profane_words():
    with open('profane_words.txt', 'r') as file:
        words = file.read().splitlines()
    return set(words)

profane_words = load_profane_words()

def is_profane(text):
    for word in profane_words:
        if re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
            return True
    return False

def load_knowledge():
    with open('exemplo.txt', 'r') as file:
        lines = file.readlines()
    knowledge = {}
    for line in lines:
        if ':' in line:
            question, answer = line.split(':', 1)
            knowledge[question.strip()] = answer.strip()
    return knowledge

def save_knowledge(question, answer):
    with open('exemplo.txt', 'a') as file:
        file.write(f"{question} : {answer}\n")

knowledge = load_knowledge()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data['message']
    
    if is_profane(message):
        reply = "Sorry, I can't process that request."
    else:
        reply = knowledge.get(message, "I don't know that. Can you tell me?")
        
        if reply == "I don't know that. Can you tell me?":
            with open('pending_questions.txt', 'a') as file:
                file.write(f"{message}\n")
    
    return jsonify({'reply': reply})

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    question = data['question']
    answer = data['answer']
    
    if is_profane(question) or is_profane(answer):
        return jsonify({'status': 'rejected', 'message': 'Content contains prohibited words.'})
    
    knowledge[question] = answer
    save_knowledge(question, answer)
    return jsonify({'status': 'updated'})

if __name__ == '__main__':
    app.run(debug=True)
