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
        
        # Set agent description first
        agent_desc = input("The other person is your...? (e.g., friend, romantic partner, brother): ").strip()
        self.chat_client.set_agent_desc(agent_desc)

        print("\nChoose the type of agent from the following options:")
        print("1. Cooperative: Focused on resolving conflicts with mutual understanding and agreement.")
        print("   Example: 'I understand why you feel this way. Let's find a solution together.'")
        print("2. Neutral: Focused on facts or maintaining balance in the conversation.")
        print("   Example: 'I didn't realize you felt this way - we haven't talked about it for a while.'")
        print("3. Competitive: Focused on asserting dominance or prioritizing personal goals.")
        print("   Example: 'I won't let this go unless you agree.'")

        # Use numbers for input
        while True:
            agent_type_input = input("Enter the number corresponding to the kind of person you want the bot to be (1, 2, or 3): ").strip()
            agent_types = {"1": "Cooperative", "2": "Neutral", "3": "Competitive"}
            if agent_type_input in agent_types:
                try:
                    self.chat_client.set_agent_type(agent_types[agent_type_input])
                    break
                except Exception as e:
                    print(e)
            else:
                print("Invalid input. Please enter 1, 2, or 3.")

        print()
        # Relationship context and situation remain unchanged
        relationship_context = input(
            "Describe them a bit more -- e.g. how long have you known them? how do they usually act? (e.g. '14 years old, We've been friends for 5 years but recently had a disagreement. He always shuts down when I try to talk to him'): "
        ).strip()
        self.chat_client.set_relationship_context(relationship_context)

        situation = input("Describe the problem you want to address (e.g., 'Setting boundaries about personal space'): ").strip()
        self.chat_client.set_situation(situation)

        self.chat_client.set_base_agent_desc()


    def run_conversation(self):
            """
            Simulate a conversation between the user and the chatbot.
            """
            print("\n--- Start Conversation ---")
            print("Available commands:")
            print("  !quit     - Exit the conversation.")
            print("  !feedback - Enter feedback mode & receive feedback.")
            print("  !resume   - Resume the conversation from feedback mode.")
            print("  !score    - See the current resolution score -- how resolved the conversation is on a scale of 1-5, where 1=unresolved, 5=resolved. Your goal is to reach 5")
            print()

            while True:
                user_input = input("You: ").strip()
                command = user_input.lower()
                
                if command == "!quit":
                    if not self.just_gave_feedback:
                        self.generate_feedback()
                        print()
                    print("Exiting conversation...")
                    if self.save_log:
                        self.save_chat_log()
                    break
                elif command == "!feedback":
                    self.generate_feedback()
                    self.just_gave_feedback = True
                    self.feedback_mode = True
                    continue
                elif command == "!resume":
                    if self.feedback_mode:
                        print("Resuming conversation...")
                        self.feedback_mode = False
                    else:
                        print("You are already in conversation mode.")
                    continue
                elif command == "!score":
                    res_score = self.chat_client.get_res_score()
                    print(f"Current resolution score: {res_score}")
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
                        category = strategies[strategy].category
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

        seperator = "-" * 15
        print(seperator)  # seperator line
        # generate & stream natural-sounding feedback based on stats report
        natural_feedback = self.chat_client.get_feedback(stats_report)
        print()

        # add feedback to chat log
        stats_str = "\n".join(stats_report)
        self.chat_log.append(f"Feedback:\n{stats_str}\n{seperator}\n{natural_feedback}")

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