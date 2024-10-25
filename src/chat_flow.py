# src/chat_flow.py: Main conversation flow for chatbot simulation

from llm import ChatClient

class ChatFlow:
    def __init__(self):
        print("Initializing ChatFlow...")
        self.chat_client = ChatClient()
        self.feedback_mode = False

    def setup_agent(self):
        """
        Configure the chatbot agent with type, description, and scenario.
        """
        print("Running setup_agent...")
        while True:
            agent_type = input("Choose agent type (Cooperative, Neutral, Competitive): ").strip()
            try:
                self.chat_client.set_agent_type(agent_type)
                break
            except Exception as e:
                print(e)

        agent_desc = input("Describe the agent (e.g., 'friend', 'romantic partner'): ").strip()
        self.chat_client.set_agent_desc(agent_desc)

        situation = input("Describe the conflict scenario (e.g., 'Setting boundaries'): ").strip()
        self.chat_client.set_situation(situation)

    def run_conversation(self):
        """
        Simulate a conversation between the user and the chatbot.
        """
        print("\n--- Start Conversation ---")
        while True:
            user_input = input("You: ")
            
            # Handle commands
            if user_input.lower() == "!quit":
                print("Exiting conversation...")
                break
            elif user_input.lower() == "!feedback":
                self.generate_feedback()
                self.feedback_mode = True
                continue
            elif user_input.lower() == "!resume":
                if self.feedback_mode:
                    print("Resuming conversation...")
                    self.feedback_mode = False
                else:
                    print("You are already in conversation mode.")
                continue

            if not self.feedback_mode:
                self.chat_client.get_response(user_input)
                print('\n')

    def generate_feedback(self):
        """
        Generate feedback or summary based on the current conversation.
        """
        print("\n--- Feedback Mode ---")
        print("Providing feedback... (Placeholder)")
        print("You can use !resume to continue the conversation or !quit to exit.")

    def start_flow(self):
        """
        Full conversation flow: setup, interaction, and report.
        """
        print("Starting conversation flow...")
        self.setup_agent()
        self.run_conversation()
        self.generate_report()

    def generate_report(self):
        """
        Generate a placeholder for a conversation summary report.
        """
        print("\n--- Conversation Summary ---")
        print("Here is your report.")

if __name__ == "__main__":
    try:
        print("Running chat_flow.py...")
        flow = ChatFlow()
        flow.start_flow()
    except Exception as e:
        print(f"An error occurred: {e}")