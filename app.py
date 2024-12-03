from flask import Flask, request, jsonify, render_template
from src.chat_flow import ChatFlow
from src.llm import strategies
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

    if agent_type not in ["Cooperative", "Neutral", "Competitive"]:
        return jsonify({"error": "Invalid agent type!"}), 400

    # Reset the ChatFlow instance
    chat_flow = ChatFlow(save_log=False)
    chat_flow.chat_client.set_agent_desc(agent_desc)
    chat_flow.chat_client.set_agent_type(agent_type)
    chat_flow.chat_client.set_relationship_context(relationship_context)
    chat_flow.chat_client.set_situation(situation)

    logger.info("Chatbot setup complete with parameters.")
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

    try:
        # Classify the user's input into a strategy
        strategy = chat_flow.chat_client.classify_strategy(user_message)

        if strategy in strategies:
            category = strategies[strategy].category
            chat_flow.user_strategy_usage[category] += 1  # Update strategy usage stats

        # Get the bot's response
        bot_response = chat_flow.chat_client.get_response(user_message, chat_flow.chat_log)

        # Update the chat log
        chat_flow.chat_log.append(f"You: {user_message}")
        chat_flow.chat_log.append(f"Bot: {bot_response}")

        return jsonify({"bot": bot_response})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/feedback", methods=["GET"])
def feedback():
    """
    Endpoint to provide feedback based on the conversation.
    """
    global chat_flow
    if not chat_flow:
        return jsonify({"error": "Chatbot is not set up yet!"}), 400

    try:
        # Generate the strategy usage statistics
        stats_report = []
        total_messages = sum(chat_flow.user_strategy_usage.values())

        for category, count in chat_flow.user_strategy_usage.items():
            if count > 0:
                percentage = (count / total_messages) * 100
                cat_stats = f"{category}: {count} times ({percentage:.2f}%)"
            else:
                cat_stats = f"{category}: Not used"
            stats_report.append(cat_stats)

        # Generate feedback using the LLM
        feedback_text = chat_flow.chat_client.get_feedback(stats_report)

        # Format the feedback for display
        final_feedback = (
            "\n".join(stats_report) +
            "\n\nSummary:\n" +
            feedback_text
        )

        return jsonify({"feedback": final_feedback})
    except Exception as e:
        return jsonify({"error": f"Feedback generation failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
