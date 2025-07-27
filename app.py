# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_system import get_transcript, create_vector_store, create_rag_chain

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for our vector stores, keyed by video ID
vector_stores = {}

@app.route('/process_video', methods=['POST'])
def process_video():
    data = request.get_json()
    youtube_url = data.get('youtube_url')
    if not youtube_url:
        return jsonify({"error": "youtube_url is required"}), 400

    video_id = youtube_url.split("v=")[1]
    
    try:
        transcript = get_transcript(youtube_url)
        vector_store = create_vector_store(transcript)
        vector_stores[video_id] = vector_store
        return jsonify({"message": "Video processed successfully", "video_id": video_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.get_json()
    video_id = data.get('video_id')
    question = data.get('question')

    if not video_id or not question:
        return jsonify({"error": "video_id and question are required"}), 400

    vector_store = vector_stores.get(video_id)
    if not vector_store:
        return jsonify({"error": "Video not processed. Please process the video first."}), 404

    try:
        rag_chain = create_rag_chain(vector_store)
        answer = rag_chain.invoke(question)
        return jsonify({"answer": answer}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)