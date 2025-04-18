from flask import Flask, render_template, request, jsonify
import ollama
from transformers import pipeline
import whisper

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")

# Load AI models
whisper_model = whisper.load_model("base")  # Load Whisper AI model for voice processing
legal_qa = pipeline("question-answering", model="nlpaueb/legal-bert-base-uncased")  # Load LegalBERT model for references

@app.route("/")
def home():
    """Render the main chatbot page."""
    return render_template("index.html")  # Make sure index.html exists in 'templates/' folder

@app.route("/get_legal_advice", methods=["POST"])
def get_legal_advice():
    """Handles user queries and provides legal advice."""
    data = request.json
    user_query = data.get("query")
    perspective = data.get("perspective", "Lawyer")  # Default to 'Lawyer' if no perspective is selected

    if not user_query:
        return jsonify({"error": "No legal query provided"}), 400

    # AI Response using Ollama (Llama3 model)
    ai_response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": f"Answer as a {perspective.lower()}: {user_query}"}]
    )["message"]["content"]

    # Legal Reference using LegalBERT
    context = "Legal cases and precedents data."
    legal_reference = legal_qa(question=user_query, context=context)["answer"]

    return jsonify({"ai_response": ai_response, "legal_reference": legal_reference})

if __name__ == "__main__":
    app.run(debug=True)
