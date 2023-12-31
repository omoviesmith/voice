from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS, cross_origin  # Import the cross_origin decorator
from process2 import insert_or_fetch_embeddings, ask_with_memory  # Import your main class or function
import os
from collections import Counter

app = Flask(__name__)
app.config['SECRET_KEY'] = "EKdeunvo.1"  # change this to a secure random string
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
CORS(app, resources={r"/*": {"origins": "https://the-voice.vercel.app", "supports_credentials": True}})

# Initialize embeddings only once
index_name = 'thevoice'
vector_store = insert_or_fetch_embeddings(index_name=index_name)  # use your actual index name

# Global list of questions asked
global_question_list = []

@app.route('/ask', methods=['POST'])
@cross_origin(supports_credentials=True)  # Apply CORS to this specific route
def ask():
    # Get the data 
    data = request.get_json()
    user_id = data.get('userId')
    question = data.get('question')

    # Update the global question list
    global_question_list.append(question)

    # Get the chat history for this user from the session
    chat_history = session.get(user_id, [])

    # Use the ask_with_memory function
    result, chat_history = ask_with_memory(vector_store, question, chat_history)

    # Save the updated chat history back to the session
    session[user_id] = chat_history

    # Return the result as JSON
    return jsonify({
        'answer': result['answer'],
        'chat_history': chat_history
    })

@app.route('/chathistory/<user_id>', methods=['GET'])
@cross_origin(supports_credentials=True)  # Apply CORS to this specific route
def get_chat_history(user_id):
    # Get the chat history for this user from the session
    chat_history = session.get(user_id, [])

    # Return the chat history as JSON
    return jsonify({
        'chat_history': chat_history
    })

@app.route('/faq', methods=['GET'])
@cross_origin()  # Apply CORS to this specific route
def frequently_asked_questions():
    # Get the top 3 most common questions from the global list
    top_common_questions = Counter(global_question_list).most_common(3)
    frequently_asked = [question for question, _ in top_common_questions]

    return jsonify({
        'frequently_asked': frequently_asked
    })

@app.route('/global-question-list', methods=['GET'])
@cross_origin()  # Apply CORS to this specific route
def get_global_question_list():
    return jsonify({
        'global_question_list': global_question_list
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
