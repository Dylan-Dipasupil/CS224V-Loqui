# CS224V-Loqui

# Loqui: A Chatbot for Practicing Healthy Conflict Resolution in Romantic and Friendship Relationships

## Overview
Loqui is an AI-powered chatbot designed to help users navigate and resolve conflicts within romantic and friendship relationships. The chatbot offers a platform for users to practice having difficult conversations in a safe, low-pressure environment, with a focus on maintaining healthy, lasting connections. By simulating various conversational scenarios and providing real-time feedback, Loqui aims to help users build confidence, improve communication skills, and learn effective conflict resolution techniques.

## Motivation
Conflicts are inevitable in relationships, but how we handle them can make all the difference. Many people struggle with navigating difficult conversations, especially when emotions are involved. Whether it's setting boundaries, apologizing, or expressing needs, practicing these conversations can help ensure relationships thrive. Loqui provides an accessible tool for users to rehearse these interactions, equipping them with the skills needed to maintain and strengthen their bonds.

## Key Features
- **Emotion and Tone Simulation**: Mimics different conversational tones, helping users prepare for various scenarios.
- **User-Directed Scenarios**: Users can specify the type of conflict and bot personality they want to practice with (e.g., setting boundaries, expressing concerns, apologizing).
- **Feedback Reports**: Provides detailed feedback on conversational patterns and suggestions for more effective communication.
- **Agent Types**: Choose from cooperative, neutral, or challenging agents for a more tailored practice experience.

---

## Installation
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/CS224V-Loqui.git
    cd CS224V-Loqui
    ```

2. **Install Requirements**:
    Ensure you have Python installed. Install dependencies with:
    ```bash
    pip install -r requirements.txt
    ```

3. **Add the Together AI API key to your environment variables**:
```
   export TOGETHER_API_KEY=a2***01
```
---

## Running Loqui

To start a conversation simulation, run the following command:

```bash
python app.py
```
To save your conversation logs, you can use the --save_log option. This will create a log file in a designated log folder, including a header detailing all the bot settings for that session.
```bash
python src/chat_flow.py --save_log
```
