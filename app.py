from flask import Flask, request, jsonify, render_template
from src.chat_flow import ChatFlow

app = Flask(__name__)

chat_flow = None

@app.route("/")
def index():
    """
    Serve the main page with the setup form and chat interface.
    """
    return render_template("index.html")

@app.route("/setup", methods=["POST"])
def setup_chat():
    """
    Endpoint to set up the chatbot with initial parameters.
    Resets the ChatFlow instance and starts fresh.
    """
    global chat_flow
    data = request.get_json()

    # Validate input data
    agent_desc = data.get("agent_desc")
    agent_type = data.get("agent_type")
    relationship_context = data.get("relationship_context")
    situation = data.get("situation")

    if not all([agent_desc, agent_type, relationship_context, situation]):
        return jsonify({"error": "All fields are required!"}), 400

    # Reset the ChatFlow instance
    chat_flow = ChatFlow(save_log=False)
    chat_flow.chat_client.set_agent_desc(agent_desc)
    chat_flow.chat_client.set_agent_type(agent_type)
    chat_flow.chat_client.set_relationship_context(relationship_context)
    chat_flow.chat_client.set_situation(situation)

    return jsonify({"message": "Chatbot setup complete!"})

@app.route("/chat", methods=["POST"])
def chat():
    """
    Endpoint to handle chat messages.
    """
    global chat_flow
    if not chat_flow:
        return jsonify({"error": "Chatbot is not set up yet!"}), 400

    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Message cannot be empty!"}), 400

    # Generate a response from the chatbot
    bot_response = chat_flow.chat_client.get_response(user_message, chat_flow.chat_log)
    chat_flow.chat_log.append(f"You: {user_message}")
    chat_flow.chat_log.append(f"Bot: {bot_response}")

    return jsonify({"bot": bot_response})

@app.route("/feedback", methods=["GET"])
def feedback():
    """
    Endpoint to provide feedback based on the conversation.
    """
    global chat_flow
    if not chat_flow:
        return jsonify({"error": "Chatbot is not set up yet!"}), 400

    # Generate feedback
    chat_flow.generate_feedback()
    feedback_messages = [log for log in chat_flow.chat_log if log.startswith("Feedback:")]
    return jsonify({"feedback": feedback_messages[-1] if feedback_messages else "No feedback yet."})

if __name__ == "__main__":
    app.run(debug=True)
