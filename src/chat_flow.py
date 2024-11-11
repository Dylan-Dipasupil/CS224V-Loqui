# src/chat_flow.py: Main conversation flow for chatbot simulation
import os
import argparse
from datetime import datetime

from llm import ChatClient, strategies, categories

LINE = "-"*40

class ChatFlow:
    def __init__(self, save_log=False):
        print("Initializing ChatFlow...")
        self.chat_client = ChatClient()
        self.feedback_mode = False
        self.chat_log = []  # Store chat messages in sequence
        self.save_log = save_log  # Toggle chat log saving
        self.user_strategy_usage = {key: 0 for key in categories.keys()}
        self.just_gave_feedback = False  

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
        
        relationship_context = input("Provide more context about your relationship (e.g., 'We've been friends for 5 years but recently had a disagreement'): ").strip()
        self.chat_client.set_relationship_context(relationship_context)

        situation = input("Describe the problem you want to address (e.g., 'Setting boundaries about personal space'): ").strip()
        self.chat_client.set_situation(situation)


    def run_conversation(self):
        """
        Simulate a conversation between the user and the chatbot.
        """
        print("\n--- Start Conversation ---")
        while True:
            user_input = input("You: ")
            
            # QUIT
            if user_input.lower() == "!quit":
                if not self.just_gave_feedback:
                    self.generate_feedback()
                    print()
                print("Exiting conversation...")
                if self.save_log:
                    self.save_chat_log()
                break
            # FEEDBACK
            elif user_input.lower() == "!feedback":
                self.generate_feedback()
                self.just_gave_feedback = True
                self.feedback_mode = True
                continue
            # RESUME
            elif user_input.lower() == "!resume":
                if self.feedback_mode:
                    print("Resuming conversation...")
                    self.feedback_mode = False
                else:
                    print("You are already in conversation mode.")
                continue

            if not self.feedback_mode and user_input:
                response = self.chat_client.get_response(user_input, self.chat_log)
                print(f"Bot: {response}")
                self.just_gave_feedback = False

                # Log the conversation turn
                self.chat_log.append(f"You: {user_input}")
                self.chat_log.append(f"Bot: {response}")

                strategy = self.chat_client.classify_strategy(user_input)
                if strategy in strategies:
                    category = strategies[strategy].category  # Find the main category
                    self.user_strategy_usage[category] += 1

            else:
                print("Please enter a valid message.")
            
            
    def generate_feedback(self):
        """
        Generate feedback or summary based on the current conversation.
        """
        print("\n--- Feedback Mode ---")

        stats_report = []

        total_messages = sum(self.user_strategy_usage.values())
        for category, count in self.user_strategy_usage.items():
            if count > 0:
                percentage = (count / total_messages) * 100
                cat_stats = f"{category}: {count} times ({percentage:.2f}%)"
            else:
                cat_stats = f"{category}: Not used"

            stats_report.append(cat_stats)
            print(cat_stats)

        print("-" * 15)  # seperator line
        # generate & stream natural-sounding feedback based on stats report
        natural_feedback = self.chat_client.get_feedback(stats_report)
        print()

        # add feedback to chat log
        stats_str = " ".join(stats_report)
        self.chat_log.append(f"Feedback:\n{stats_str}\n\n{natural_feedback}")

        print("You can use !resume to continue the conversation or !quit to exit.")


    def start_flow(self):
        """
        Full conversation flow: setup, interaction, and report.
        """
        print("Starting conversation flow...")
        self.setup_agent()
        self.run_conversation()

    
    def save_chat_log(self):
        """
        Save the chat log to a timestamped text file in a 'logs' folder.
        """
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("Y%Y_M%m_D%d_H%H_M%M_S%S")
        filename = f"{log_dir}/chat_log_{timestamp}.txt"

        # Pull agent configuration from self.chat_client
        header = [
            "Chat Log Summary:",
            f"Agent Type: {self.chat_client.agent_type}",
            f"Agent Description: {self.chat_client.agent_desc}",
            f"Relationship Context: {self.chat_client.relationship_context}",
            f"Conflict Scenario: {self.chat_client.situation}",
            LINE  # Separator line
        ]

        # Combine header and chat log
        full_log = header + self.chat_log

        # Write the header and chat log to file
        with open(filename, "w") as file:
            file.write("\n".join(full_log))
        
        print(f"Chat log saved to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Loqui chatbot.")
    parser.add_argument("--save_log", action="store_true", help="Enable chat log saving")
    args = parser.parse_args()

    try:
        print("Starting Loqui...")
        flow = ChatFlow(save_log=args.save_log)
        flow.start_flow()
    except KeyboardInterrupt:
        if flow.save_log:
            flow.save_chat_log()
    except Exception as e:
        print(f"An error occurred: {e}")